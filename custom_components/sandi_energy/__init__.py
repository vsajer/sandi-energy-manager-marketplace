"""Independent coordinator for SANDI energy data, EV charging and hot water."""

from functools import partial
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.start import async_at_started

from .const import DOMAIN
from .controller import EnergyController

PLATFORMS = [Platform.SENSOR]
PANEL_PATH = "sandi-energy"
PANEL_ASSET = "/sandi_energy_assets/energy-panel.js"


async def async_setup(hass, config):
    """Serve the bundled JavaScript once per Home Assistant process."""
    await hass.http.async_register_static_paths([
        StaticPathConfig(PANEL_ASSET, str(Path(__file__).with_name("energy-panel.js")), False)
    ])
    return True


async def async_setup_entry(hass, entry):
    controller = entry.runtime_data = EnergyController(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    registry = er.async_get(hass)
    diagnostics = {
        key: registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
        or f"sensor.sandi_energy_{key}"
        for key in ("ev", "boiler", "outlets")
    }
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name="sandi-energy-panel",
        sidebar_title="Energie domu",
        sidebar_icon="mdi:solar-power",
        module_url=f"{PANEL_ASSET}?v=0.2.0",
        config={
            "entities": dict(entry.data),
            "diagnostics": diagnostics,
            "eps_limit_w": controller.config["inverter_limit_w"],
        },
        require_admin=True,
    )
    entry.async_on_unload(partial(frontend.async_remove_panel, hass, PANEL_PATH))
    entry.async_on_unload(async_at_started(hass, controller.start))
    return True


async def async_unload_entry(hass, entry):
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    await entry.runtime_data.stop()
    return True
