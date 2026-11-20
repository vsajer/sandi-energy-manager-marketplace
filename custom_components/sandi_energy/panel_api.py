"""Administrator-only settings actions for the Energie domu panel."""

try:
    import probatio as vol
except ImportError:
    import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import Context, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers import entity_registry as er

from .const import CONTROL_DEFAULTS, CONTROL_RANGES, DOMAIN, ENTITY_DOMAINS, OUTLET_DEFAULTS, OUTLET_RANGES
from .outlets import NON_OUTLET_METERS, valid_outlet_meter

OUTLET_SCHEMA = vol.Schema({
    vol.Required("enabled"): bool,
    vol.Optional("power_sensor"): str,
    **{vol.Required(key): vol.All(int, vol.Range(min=minimum, max=maximum))
       for key, (minimum, maximum) in OUTLET_RANGES.items()},
})
CONTROLS_SCHEMA = vol.Schema({
    **{vol.Required(key): bool for key, value in CONTROL_DEFAULTS.items() if type(value) is bool},
    vol.Required("phases"): vol.In((1, 3)),
    **{vol.Required(key): vol.All(int, vol.Range(min=low, max=high))
       for key, (low, high) in CONTROL_RANGES.items()},
})


@callback
def async_register_commands(hass):
    websocket_api.async_register_command(hass, read_outlets)
    websocket_api.async_register_command(hass, write_outlet)
    websocket_api.async_register_command(hass, read_controls)
    websocket_api.async_register_command(hass, write_controls)
    websocket_api.async_register_command(hass, command_device)
    websocket_api.async_register_command(hass, subscribe_entities)
    websocket_api.async_register_command(hass, write_entity)
    websocket_api.async_register_command(hass, subscribe_audit)


def _loaded_entry(hass, connection, msg):
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN or entry.state is not ConfigEntryState.LOADED:
        connection.send_error(msg["id"], "not_found", "Integrace není právě načtená.")
        return None
    return entry


def _result(entry):
    return {
        "outlets": entry.options.get("outlets", []),
        "defaults": OUTLET_DEFAULTS,
        "excluded": [entity for key in ("source", "session") if (entity := entry.data.get(key))],
    }


def _controls(entry):
    return {key: entry.options.get(key, default) for key, default in CONTROL_DEFAULTS.items()}


def _entity_settings(entry):
    return {
        "mapping": {role: entry.data.get(role) for role in ENTITY_DOMAINS},
        "domains": ENTITY_DOMAINS,
        "watched": entry.options.get("watched_entities", []),
    }


@callback
@websocket_api.require_admin
@websocket_api.websocket_command({"type": "sandi_energy/entities/subscribe", vol.Required("entry_id"): str})
def subscribe_entities(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return

    @callback
    def send_settings():
        connection.send_event(msg["id"], _entity_settings(entry))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, f"{DOMAIN}_entities_{entry.entry_id}", send_settings
    )
    connection.send_result(msg["id"])
    send_settings()


@callback
@websocket_api.require_admin
@websocket_api.websocket_command({"type": "sandi_energy/audit/subscribe", vol.Required("entry_id"): str})
def subscribe_audit(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return
    audit = entry.runtime_data.audit

    @callback
    def send_record(payload):
        connection.send_event(msg["id"], payload)

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, audit.signal, send_record)
    connection.send_result(msg["id"])
    send_record({"history": audit.records})


def _validate_assignment(entry, role, entity):
    domain = ENTITY_DOMAINS[role]
    if not entity or not entity.startswith(f"{domain}."):
        raise ValueError(f"Vyber entitu typu {domain}.")
    for group in (("source", "session"), ("solar_enabled", "night_enabled")):
        if role in group and any(entity == entry.data.get(key) for key in group if key != role):
            raise ValueError("Pro tyto dvě role vyber různé entity.")
    outlets = entry.options.get("outlets", [])
    if domain == "switch" and any(item["entity"] == entity for item in outlets):
        raise ValueError("Spínač je už přiřazený jako solární zásuvka.")
    if role in NON_OUTLET_METERS and any(item.get("power_sensor") == entity for item in outlets):
        raise ValueError("Senzor už měří příkon solární zásuvky.")
    control = {"source": "control_ev", "session": "control_ev", "current": "control_ev",
               "boiler": "control_boiler"}.get(role)
    if control and entry.options.get(control):
        raise ValueError("Před změnou ovládané entity vypni její automatické řízení v regulátoru.")


@websocket_api.require_admin
@websocket_api.websocket_command({
    "type": "sandi_energy/entities/save", vol.Required("entry_id"): str,
    vol.Required("role"): vol.Any(vol.In(tuple(ENTITY_DOMAINS)), None),
    vol.Required("expected"): vol.Any(str, None), vol.Required("entity"): vol.Any(str, None),
})
@websocket_api.async_response
async def write_entity(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return
    role, expected, entity = msg["role"], msg["expected"], msg["entity"]
    controller = entry.runtime_data
    async with controller.action_lock:
        if entry.state is not ConfigEntryState.LOADED or entry.runtime_data is not controller:
            connection.send_error(msg["id"], "conflict", "Integrace se právě načítá. Zkus to znovu.")
            return
        watched = entry.options.get("watched_entities", [])
        if ((role is not None and entry.data.get(role) != expected)
                or (role is None and expected is not None and expected not in watched)):
            connection.send_error(msg["id"], "conflict", "Entita se mezitím změnila. Otevři úpravu znovu.")
            return
        try:
            if entity != expected:
                if entity is not None and hass.states.get(entity) is None and er.async_get(hass).async_get(entity) is None:
                    raise ValueError("Vyber existující entitu Home Assistantu.")
                if role is not None:
                    _validate_assignment(entry, role, entity)
                elif entity in watched:
                    raise ValueError("Tato entita už je v seznamu sledovaných.")
        except ValueError as err:
            connection.send_error(msg["id"], "invalid_format", str(err))
            return

        if entity != expected:
            if role is not None:
                data = {**entry.data, role: entity}
                if hass.config_entries.async_update_entry(entry, data=data):
                    controller.apply_entities(data, role)
            else:
                updated = [entity if item == expected else item for item in watched
                           if item != expected or entity is not None]
                if expected is None:
                    updated.append(entity)
                hass.config_entries.async_update_entry(entry, options={**entry.options, "watched_entities": updated})
            if role is not None:
                action = "entity_assign"
            elif entity is None:
                action = "watch_remove"
            else:
                action = "watch_add" if expected is None else "watch_change"
            controller.audit.record("settings", action, entity or expected, details={"role": role, "previous": expected})
            async_dispatcher_send(hass, f"{DOMAIN}_entities_{entry.entry_id}")
        connection.send_result(msg["id"])


@callback
@websocket_api.require_admin
@websocket_api.websocket_command({"type": "sandi_energy/controls", vol.Required("entry_id"): str})
def read_controls(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is not None:
        connection.send_result(msg["id"], {"values": _controls(entry), "ranges": CONTROL_RANGES})


@websocket_api.require_admin
@websocket_api.websocket_command({
    "type": "sandi_energy/controls/save", vol.Required("entry_id"): str,
    vol.Required("expected"): dict, vol.Required("settings"): dict,
})
@websocket_api.async_response
async def write_controls(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return
    try:
        settings = CONTROLS_SCHEMA(msg["settings"])
        if any(type(settings[key]) is not type(default) for key, default in CONTROL_DEFAULTS.items()):
            raise ValueError
    except (vol.Invalid, ValueError):
        connection.send_error(msg["id"], "invalid_format", "Zkontroluj hodnoty a jejich rozsahy.")
        return
    if settings["control_source"] and not settings["control_ev"]:
        connection.send_error(msg["id"], "invalid_format", "Přepínání přes IN Grid relé vyžaduje automatiku nabíječky EV.")
        return

    controller = entry.runtime_data
    async with controller.action_lock:
        if entry.state is not ConfigEntryState.LOADED or entry.runtime_data is not controller:
            connection.send_error(msg["id"], "conflict", "Integrace se právě načítá. Zkus to znovu.")
            return
        if _controls(entry) != msg["expected"]:
            connection.send_error(msg["id"], "conflict", "Nastavení se mezitím změnilo. Otevři ho znovu.")
            return
        previous = _controls(entry)
        if hass.config_entries.async_update_entry(entry, options={**entry.options, **settings}):
            controller.apply_controls(settings)
            changes = {key: value for key, value in settings.items() if value != previous[key]}
            if changes:
                controller.audit.record("settings", "controls_save", details=changes)
        connection.send_result(msg["id"], {"values": _controls(entry), "ranges": CONTROL_RANGES})


@websocket_api.require_admin
@websocket_api.websocket_command({
    "type": "sandi_energy/device/command", vol.Required("entry_id"): str,
    vol.Required("command"): str, vol.Optional("value"): vol.Any(bool, int, float, str),
    vol.Required("mapping"): dict,
})
@websocket_api.async_response
async def command_device(hass, connection, msg):
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return
    try:
        await entry.runtime_data.run_manual(
            msg["command"], msg.get("value"), Context(user_id=connection.user.id), mapping=msg["mapping"]
        )
    except ValueError as err:
        connection.send_error(msg["id"], "command_refused", str(err))
        return
    connection.send_result(msg["id"])


@callback
@websocket_api.require_admin
@websocket_api.websocket_command({"type": "sandi_energy/outlets", vol.Required("entry_id"): str})
def read_outlets(hass, connection, msg):
    """Read current outlet settings."""
    if (entry := _loaded_entry(hass, connection, msg)) is not None:
        connection.send_result(msg["id"], _result(entry))


@callback
@websocket_api.require_admin
@websocket_api.websocket_command({
    "type": "sandi_energy/outlets/save", vol.Required("entry_id"): str, vol.Required("entity"): str,
    vol.Required("expected"): vol.Any(dict, None), vol.Required("settings"): vol.Any(dict, None),
})
def write_outlet(hass, connection, msg):
    """Save a single outlet, protecting it against edits in another tab."""
    if (entry := _loaded_entry(hass, connection, msg)) is None:
        return
    entity = msg["entity"]
    outlets = entry.options.get("outlets", [])
    current = next((item for item in outlets if item["entity"] == entity), None)
    if current != msg["expected"]:
        connection.send_error(msg["id"], "conflict", "Nastavení se mezitím změnilo. Otevři zásuvku znovu.")
        return

    settings = msg["settings"]
    if settings is not None:
        if (not entity.startswith("switch.") or entity in _result(entry)["excluded"]
                or (current is None and hass.states.get(entity) is None
                    and er.async_get(hass).async_get(entity) is None)):
            connection.send_error(msg["id"], "invalid_format", "Vyber dostupný spínač zásuvky.")
            return
        try:
            settings = OUTLET_SCHEMA(settings)
            if any(type(settings[key]) is not int for key in OUTLET_RANGES):
                raise ValueError
        except (vol.Invalid, ValueError):
            connection.send_error(msg["id"], "invalid_format", "Zkontroluj prioritu, příkon a časové limity.")
            return

    updated = [item for item in outlets if item["entity"] != entity]
    if settings is not None:
        meter = settings.get("power_sensor")
        if meter and not valid_outlet_meter(hass.states, entry.data, updated, meter,
                                           (current or {}).get("power_sensor")):
            connection.send_error(msg["id"], "invalid_format", "Vyber samostatný senzor příkonu ve W nebo kW.")
            return
        replacement = {**settings, "entity": entity}
        if current == replacement:
            connection.send_result(msg["id"], _result(entry))
            return
        updated.append(replacement)
    if hass.config_entries.async_update_entry(entry, options={**entry.options, "outlets": updated}):
        entry.runtime_data.apply_outlets(updated)
        action = "outlet_remove" if settings is None else "outlet_edit" if current else "outlet_add"
        entry.runtime_data.audit.record("settings", action, entity, details=settings)
    connection.send_result(msg["id"], _result(entry))
