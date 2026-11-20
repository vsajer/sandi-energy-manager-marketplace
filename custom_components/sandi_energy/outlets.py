"""Dispatch solar outlets by priority, with one switch transition per pass."""

from dataclasses import dataclass

START_MARGIN_W = 200
START_STABLE_SECONDS = 30
POWER_UNITS = {"W": 1, "kW": 1000}
NON_OUTLET_METERS = ("pv", "eps", "overload", "ev_power")


def valid_outlet_meter(states, entities, other_outlets, meter, previous=None):
    if not isinstance(meter, str) or not meter.startswith("sensor."):
        return False
    if meter in {entities.get(name) for name in NON_OUTLET_METERS}:
        return False
    if any(item.get("power_sensor") == meter for item in other_outlets):
        return False
    state = states.get(meter)
    return meter == previous or (state is not None and state.attributes.get("unit_of_measurement") in POWER_UNITS)


@dataclass(frozen=True)
class Outlet:
    entity: str
    priority: int
    watts: int
    enabled: bool
    min_on_s: int
    min_off_s: int
    on: bool | None
    age: float
    power_sensor: str | None = None
    measured_w: float | None = None

    @property
    def draw_w(self):
        return self.measured_w if self.on and self.measured_w is not None else self.watts


@dataclass(frozen=True)
class OutletPlan:
    targets: frozenset[str]
    turn_on: str | None = None
    turn_off: str | None = None
    reason: str = ""


def ranked_outlets(outlets):
    return sorted(
        (item for item in outlets if item.enabled and item.on is not None),
        key=lambda item: (-item.priority, item.entity),
    )


def keep_running(item, overload):
    return item.on and not overload and (item.priority >= 0 or item.age < item.min_on_s)


def outlet_requirement(item):
    if item.on:
        return item.draw_w
    if item.age >= item.min_off_s:
        return item.watts + START_MARGIN_W
    return None


def plan_outlets(outlets: list[Outlet], pv_w: float | None, eps_w: float | None,
                 reserve_w: int, limit_w: int) -> OutletPlan:
    ranked = ranked_outlets(outlets)
    running = [item for item in ranked if item.on]
    current_targets = frozenset(item.entity for item in running)
    overload = eps_w is not None and eps_w > limit_w
    if overload and running:
        return OutletPlan(current_targets - {running[-1].entity}, turn_off=running[-1].entity,
                          reason="Překročený limit EPS")
    if pv_w is None or eps_w is None:
        return OutletPlan(current_targets, reason="Čekám na platná měření FVE a EPS")

    measured_headroom = min(pv_w - eps_w - reserve_w, limit_w - eps_w)
    locked = [item for item in running if keep_running(item, overload)]
    targets = {item.entity for item in locked}
    budget = measured_headroom + min(eps_w, sum(item.draw_w for item in running)) - sum(item.draw_w for item in locked)
    for item in ranked:
        if item.entity in targets:
            continue
        need = outlet_requirement(item)
        if need is not None and budget >= need:
            targets.add(item.entity)
            budget -= item.draw_w
    return dispatch_outlets(ranked, targets, measured_headroom)


def dispatch_outlets(ranked, targets, measured_headroom):
    desired = frozenset(targets)
    for item in reversed(ranked):
        if item.on and item.entity not in desired:
            return OutletPlan(desired, turn_off=item.entity,
                              reason="Uvolňuji výkon podle priorit")
    for item in ranked:
        if not item.on and item.entity in desired:
            if measured_headroom >= item.watts + START_MARGIN_W:
                return OutletPlan(desired, turn_on=item.entity, reason="Dostatek FV přebytku")
            return OutletPlan(desired, reason="Čekám na naměřenou výkonovou rezervu")
    return OutletPlan(desired, reason="Zásuvky odpovídají dostupnému výkonu a prioritám")
