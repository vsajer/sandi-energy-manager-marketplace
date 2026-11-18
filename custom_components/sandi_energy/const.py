"""Supported entity domains and defaults."""

DOMAIN = "sandi_energy"
VERSION = "0.5.0"

PRIORITY_RANGE = (-5, 5)
GROUP_PRIORITIES = ("ev_priority", "boiler_priority", "outlet_priority")
OUTLET_DEFAULTS = {"enabled": False, "priority": -1, "watts": 500, "min_on_s": 120, "min_off_s": 60}
OUTLET_RANGES = {"priority": PRIORITY_RANGE, "watts": (1, 20000), "min_on_s": (0, 86400), "min_off_s": (0, 86400)}

ENTITY_DOMAINS = {
    "pv": "sensor",
    "eps": "sensor",
    "overload": "sensor",
    "soc": "sensor",
    "eta": "sensor",
    "ev_power": "sensor",
    "ev_status": "sensor",
    "connected": "binary_sensor",
    "tariff": "binary_sensor",
    "solar_enabled": "input_boolean",
    "night_enabled": "input_boolean",
    "source": "switch",
    "session": "switch",
    "current": "number",
    "boiler": "climate"
}

CONTROL_DEFAULTS = {
    "control_ev": False,
    "control_source": False,
    "sonoff_on_is_solar": True,
    "control_boiler": False,
    "control_outlets": False,
    "ev_priority": -1,
    "boiler_priority": -2,
    "outlet_priority": -3,
    "boiler_w": 2000,
    "phases": 1,
    "solar_max_a": 16,
    "night_a": 6,
    "pv_reserve_w": 3000,
    "inverter_limit_w": 5500,
    "power_max_age_s": 180,
}

CONTROL_RANGES = {
    "solar_max_a": (6, 32), "night_a": (6, 32), "pv_reserve_w": (0, 20000),
    "inverter_limit_w": (1000, 50000), "power_max_age_s": (15, 600),
    "boiler_w": (1, 10000),
    **dict.fromkeys(GROUP_PRIORITIES, PRIORITY_RANGE),
}
