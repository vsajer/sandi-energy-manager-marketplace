"""Administrator-only settings actions for the Energie domu panel."""

try:
    import probatio as vol
except ImportError:
    import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, OUTLET_DEFAULTS, OUTLET_RANGES

OUTLET_SCHEMA = vol.Schema({
    vol.Required("enabled"): bool,
    **{vol.Required(key): vol.All(int, vol.Range(min=minimum, max=maximum))
       for key, (minimum, maximum) in OUTLET_RANGES.items()},
})


@callback
def async_register_commands(hass):
    websocket_api.async_register_command(hass, read_outlets)
    websocket_api.async_register_command(hass, write_outlet)


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
        "excluded": [entry.data["source"], entry.data["session"]],
    }


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
        updated.append({**settings, "entity": entity})
    if hass.config_entries.async_update_entry(entry, options={**entry.options, "outlets": updated}):
        entry.runtime_data.apply_outlets(updated)
    connection.send_result(msg["id"], _result(entry))
