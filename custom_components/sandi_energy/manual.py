"""Resolve explicit panel actions against current entity states and load limits."""

from math import isclose, isfinite
from time import monotonic

from .policy import KNOWN_STATUSES, MIN_A, SOURCE_SETTLE_SECONDS

HELPERS = {"solar_mode": "solar_enabled", "night_mode": "night_enabled"}
EV_COMMANDS = {"ev_start", "ev_stop", "ev_current"}


def manual_service(controller, command, value):
    """Return a validated service call for a known action and configured target."""
    if command in HELPERS:
        key = HELPERS[command]
        if type(value) is not bool or controller._flag(key) is None:
            raise ValueError("Přepínač režimu není dostupný.")
        return key, "turn_on" if value else "turn_off", {}
    if command in EV_COMMANDS:
        if controller.config["control_ev"]:
            raise ValueError("Nabíječku právě řídí automatika. Pro ruční povel ji vypni v nastavení panelu.")
        return _ev_service(controller, command, value)
    if command in {"boiler_on", "boiler_off", "boiler_preset"}:
        if controller.config["control_boiler"]:
            raise ValueError("Bojler právě řídí automatika. Pro ruční povel ji vypni v nastavení panelu.")
        return _boiler_service(controller, command, value)
    raise ValueError("Neznámý povel.")


def _ev_service(controller, command, value):
    session = controller._flag("session")
    if session is None:
        raise ValueError("Spínač nabíjecí relace není dostupný.")
    if command == "ev_stop":
        return "session", "turn_off", {}

    observed = controller._numeric("current")
    if observed is None:
        raise ValueError("Nastavený proud nabíječky není dostupný.")
    requested = observed if command == "ev_start" else value
    if (type(requested) not in (int, float) or not isfinite(requested) or requested < MIN_A
            or (supported := controller._supported_current(requested)) is None
            or not isclose(requested, supported)):
        raise ValueError("Proud musí odpovídat rozsahu a kroku nabíječky, nejméně 6 A.")
    if command == "ev_start" or (session and requested > observed):
        _check_ev_capacity(controller, requested, session)
    if command == "ev_start":
        return "session", "turn_on", {}
    return "current", "set_value", {"value": requested}


def _check_ev_capacity(controller, amps, session):
    status = controller._value("ev_status")
    if (controller._flag("connected") is not True or status not in KNOWN_STATUSES - {"fault", "charged"}
            or not session and status == "charging"):
        raise ValueError("Připojení auta a stav nabíječky musí umožňovat nabíjení.")
    source = controller._flag("source")
    if (source is None or controller._age("source") < SOURCE_SETTLE_SECONDS
            or monotonic() < controller._source_pending_until):
        raise ValueError("Čekám na dostupnou a ustálenou polohu zdroje.")
    if source != controller.config["sonoff_on_is_solar"]:
        return

    pv = controller._power("pv")
    eps = controller._eps()
    ev = controller._power("ev_power") if session else 0
    if None in (pv, eps, ev):
        raise ValueError("Pro nabíjení z FVE chybí čerstvá měření výkonu.")
    house = max(0, eps - ev)
    available = min(pv - house - controller.config["pv_reserve_w"],
                    controller.config["inverter_limit_w"] - house)
    if amps * 230 * controller.config["phases"] > available:
        raise ValueError("Pro zvolený proud není dostatečná rezerva FVE nebo EPS.")


def _boiler_service(controller, command, value):
    state = controller._state("boiler")
    if state is None or controller._value("boiler") is None:
        raise ValueError("Termostat bojleru není dostupný.")
    if command == "boiler_off":
        return "boiler", "turn_off", {}
    if command == "boiler_preset" and (value not in ("activity", "eco", "sleep")
                                       or value not in state.attributes.get("preset_modes", [])):
        raise ValueError("Termostat tento preset nenabízí.")
    if command == "boiler_on" or value in ("activity", "eco"):
        eps = controller._eps()
        limit = min(4000, controller.config["inverter_limit_w"])
        added = 0 if state.attributes.get("hvac_action") == "heating" else controller.config["boiler_w"]
        if eps is None or eps + added > limit:
            raise ValueError("Bojler nelze zapnout bez potvrzené rezervy na EPS.")
    if command == "boiler_on":
        return "boiler", "turn_on", {}
    return "boiler", "set_preset_mode", {"preset_mode": value}
