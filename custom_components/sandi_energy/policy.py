"""Deterministic energy rules with no Home Assistant dependencies."""

from dataclasses import dataclass
from math import floor

IDLE_STATUSES = frozenset({"charged", "plugged_in", "idle", "sleep", "waiting", "paused"})
KNOWN_STATUSES = IDLE_STATUSES | {"charging", "fault"}
MIN_A = 6
NIGHT_TARIFF_DELAY = 600
SOURCE_IDLE_SECONDS = 10
SOURCE_SETTLE_SECONDS = 20
SOLAR_INCREASE_SECONDS = 30
SOLAR_RESTART_RESERVE_W = 350


@dataclass(frozen=True)
class EVInput:
    solar: bool | None
    night: bool | None
    tariff: bool | None
    tariff_age: float
    connected: bool | None
    status: str | None
    session: bool | None
    source_solar: bool | None
    pv_w: float | None
    eps_w: float | None
    ev_w: float | None
    soc: float | None


@dataclass(frozen=True)
class EVPlan:
    mode: str
    reason: str
    source_solar: bool | None = None
    amps: int | None = None
    available_w: float | None = None


def plan_ev(data: EVInput, config: dict) -> EVPlan:
    """Calculate the desired source and charging current, using 0 A for stop."""
    if data.solar is False and data.night is False:
        return EVPlan("manual", "Oba automatické režimy jsou vypnuté")
    if data.solar is not True and data.night is not True:
        return EVPlan("waiting", "Přepínače režimu nejsou dostupné")

    if data.night and data.tariff is not False:
        if data.tariff is None or data.tariff_age < NIGHT_TARIFF_DELAY:
            return EVPlan("waiting", "Čekám na potvrzený nízký tarif", amps=0)
        mode, source_solar = "night", False
    elif data.solar:
        mode, source_solar = "solar", True
    else:
        # The default source outside a night session is solar, as in the old YAML.
        return EVPlan("waiting", "Mimo nízký tarif", source_solar=True, amps=0)

    if data.connected is not True:
        return EVPlan(mode, "Připojení auta není potvrzené", amps=0)
    if data.status not in KNOWN_STATUSES or data.status in {"fault", "charged"}:
        return EVPlan(mode, "Nabíječka hlásí konec, poruchu nebo neznámý stav", amps=0)
    if mode == "night":
        return EVPlan(mode, "Nízký tarif je aktivní", source_solar, config["night_a"])

    if None in (data.pv_w, data.eps_w, data.ev_w, data.soc, data.source_solar):
        return EVPlan(mode, "Chybí platná měření FVE, baterie nebo zdroje", amps=0)
    if not 0 <= data.soc <= 100:
        return EVPlan(mode, "Neplatné procento nabití domácí baterie", amps=0)
    if data.session is None:
        return EVPlan(mode, "Stav nabíjecí relace není dostupný", amps=0)
    ongoing_solar = data.session and data.source_solar
    if data.soc < (50 if ongoing_solar else 90):
        return EVPlan(mode, "Nízké nabití domácí baterie", source_solar, 0)

    house_w = max(0, data.eps_w - data.ev_w) if data.source_solar else data.eps_w
    available_w = min(data.pv_w - house_w - config["pv_reserve_w"],
                      config["inverter_limit_w"] - house_w)
    watts_per_amp = 230 * config["phases"]
    minimum = MIN_A * watts_per_amp
    if not ongoing_solar:
        minimum += SOLAR_RESTART_RESERVE_W
    if available_w < minimum:
        return EVPlan(mode, "Nedostatek FV přebytku", source_solar, 0, available_w)
    amps = min(config["solar_max_a"], floor(available_w / watts_per_amp))
    return EVPlan(mode, "Dostatečný FV přebytek", source_solar, amps, available_w)


def boiler_preset(hour: int, eta_minutes: float | None) -> str | None:
    """Select the scheduled preset with complete ETA bands."""
    if hour < 10 or hour >= 21:
        return "sleep"
    if eta_minutes is None or eta_minutes < 0:
        return None
    if hour < 12:
        return "activity" if eta_minutes < 120 else "sleep"
    if eta_minutes < 20:
        return "activity"
    return "eco" if eta_minutes < 50 else "sleep"
