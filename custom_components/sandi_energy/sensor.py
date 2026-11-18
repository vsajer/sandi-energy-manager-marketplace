"""Expose the decisions as dashboard and automation inputs."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        DecisionSensor(entry, "ev", "SANDI Energy EV", "mdi:ev-station"),
        DecisionSensor(entry, "boiler", "SANDI Energy Boiler", "mdi:water-boiler"),
        DecisionSensor(entry, "outlets", "SANDI Energy Outlets", "mdi:power-socket-eu"),
    ])


class DecisionSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, entry, key, name, icon):
        self.controller = entry.runtime_data
        self.key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.controller.listeners.append(self._updated)
        self.async_on_remove(lambda: self.controller.listeners.remove(self._updated))

    @callback
    def _updated(self):
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self.controller.diagnostics[self.key].get("state")

    @property
    def extra_state_attributes(self):
        return {key: value for key, value in self.controller.diagnostics[self.key].items()
                if key != "state"}
