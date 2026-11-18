"""Independent coordinator for SANDI energy data, EV charging and hot water."""

from homeassistant.const import Platform
from homeassistant.helpers.start import async_at_started

from .controller import EnergyController

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    controller = entry.runtime_data = EnergyController(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(async_at_started(hass, controller.start))
    return True


async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    await entry.runtime_data.stop()
    return True
