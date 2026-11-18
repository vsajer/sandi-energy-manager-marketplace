"""Set up entity mapping and opt in to individual controls."""

try:
    import probatio as vol
except ImportError:
    import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import CONTROL_DEFAULTS, CONTROL_RANGES, DOMAIN, ENTITY_DOMAINS, OUTLET_DEFAULTS, OUTLET_RANGES


def entity_schema(values: dict):
    return vol.Schema({
        vol.Required(key, **({"default": values[key]} if key in values else {})): EntitySelector(
            EntitySelectorConfig(domain=domain)
        )
        for key, domain in ENTITY_DOMAINS.items()
    })


LIMITS = {
    "phases": vol.All(vol.Coerce(int), vol.In((1, 3))),
    **{key: vol.All(vol.Coerce(int), vol.Range(min=low, max=high))
       for key, (low, high) in CONTROL_RANGES.items()},
}


class SandiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Install one controller for the household."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self._entity_form("user", {}, user_input)

    async def async_step_reconfigure(self, user_input=None):
        entry = self._get_reconfigure_entry()
        return self._entity_form("reconfigure", entry.data, user_input, entry)

    def _entity_form(self, step, defaults, user_input, entry=None):
        errors = {}
        if user_input is not None:
            if user_input["session"] == user_input["source"]:
                errors["source"] = "entities_conflict"
            elif entry is not None:
                return self.async_update_reload_and_abort(entry, data_updates=user_input)
            else:
                return self.async_create_entry(title="SANDI Energy Manager", data=user_input)
        return self.async_show_form(step_id=step, data_schema=entity_schema(user_input or defaults),
                                    errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SandiOptionsFlow()


class SandiOptionsFlow(OptionsFlowWithReload):
    """Configure operating limits and which actuators are enabled."""

    async def async_step_init(self, user_input=None):
        self._saved = dict(self.config_entry.options)
        self._outlets = list(self._saved.get("outlets", []))
        menu = ["operating", "add_outlet"]
        if self._outlets:
            menu.extend(("edit_outlet", "remove_outlet"))
        return self.async_show_menu(step_id="init", menu_options=menu)

    async def async_step_operating(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input["control_source"] or user_input["control_ev"]:
                return self.async_create_entry(data={**self.config_entry.options, **user_input})
            errors["control_source"] = "source_requires_ev"

        values = {**CONTROL_DEFAULTS, **self._saved, **(user_input or {})}
        schema = vol.Schema({
            vol.Required(key, default=values[key]): LIMITS.get(key, bool)
            for key in CONTROL_DEFAULTS
        })
        return self.async_show_form(step_id="operating", data_schema=schema, errors=errors)

    async def async_step_add_outlet(self, user_input=None):
        self._selected = None
        return await self.async_step_outlet(user_input)

    async def async_step_edit_outlet(self, user_input=None):
        if user_input is not None:
            self._selected = user_input["entity"]
            return await self.async_step_outlet()
        return self._pick_outlet("edit_outlet")

    async def async_step_remove_outlet(self, user_input=None):
        if user_input is not None:
            current = self.config_entry.options.get("outlets", [])
            return self._save_outlets([x for x in current if x["entity"] != user_input["entity"]])
        return self._pick_outlet("remove_outlet")

    def _pick_outlet(self, step):
        options = {x["entity"]: x["entity"] for x in self._outlets}
        return self.async_show_form(step_id=step, data_schema=vol.Schema({
            vol.Required("entity"): vol.In(options),
        }))

    def _save_outlets(self, outlets):
        return self.async_create_entry(data={**self.config_entry.options, "outlets": outlets})

    async def async_step_outlet(self, user_input=None):
        errors = {}
        other = [x for x in self.config_entry.options.get("outlets", []) if x["entity"] != self._selected]
        if user_input is not None:
            reserved = {self.config_entry.data["session"], self.config_entry.data["source"]}
            if user_input["entity"] in reserved | {x["entity"] for x in other}:
                errors["entity"] = "outlet_reserved"
            else:
                return self._save_outlets([*other, user_input])

        current = next((x for x in self._outlets if x["entity"] == self._selected), {})
        values = {**current, **(user_input or {})}
        schema = vol.Schema({
            vol.Required("entity"): EntitySelector(EntitySelectorConfig(domain="switch")),
            vol.Required("enabled", default=True): bool,
            **{vol.Required(key, default=OUTLET_DEFAULTS[key]): vol.All(
                vol.Coerce(int), vol.Range(min=minimum, max=maximum)
            ) for key, (minimum, maximum) in OUTLET_RANGES.items()},
        })
        return self.async_show_form(
            step_id="outlet", data_schema=self.add_suggested_values_to_schema(schema, values),
            errors=errors,
        )
