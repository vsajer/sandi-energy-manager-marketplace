"""Dispatch solar outlets by priority, with one switch transition per pass."""

from dataclasses import dataclass

START_MARGIN_W = 200
START_STABLE_SECONDS = 30


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


@dataclass(frozen=True)
class OutletPlan:
    targets: frozenset[str]
    turn_on: str | None = None
    turn_off: str | None = None
    reason: str = ""


def plan_outlets(outlets: list[Outlet], pv_w: float | None, eps_w: float | None,
                 reserve_w: int, limit_w: int, allocation_w: float | None = None) -> OutletPlan:
    ranked = sorted(
        (item for item in outlets if item.enabled and item.on is not None),
        key=lambda item: (-item.priority, item.entity),
    )
    running = [item for item in ranked if item.on]
    current_targets = frozenset(item.entity for item in running)
    overload = eps_w is not None and eps_w > limit_w
    if overload and running and allocation_w is None:
        return OutletPlan(current_targets - {running[-1].entity}, turn_off=running[-1].entity,
                          reason="Překročený limit EPS")
    if pv_w is None or eps_w is None:
        return OutletPlan(current_targets, reason="Čekám na platná měření FVE a EPS")

    # Nominal consumption is used for ranking already running outlets only.
    # Before turning anything on, require headroom against the actual EPS reading.
    measured_headroom = min(pv_w - eps_w - reserve_w, limit_w - eps_w)
    load_w = sum(item.watts for item in running)
    budget = (measured_headroom + min(eps_w, load_w)
              if allocation_w is None else allocation_w)
    targets = set()
    for item in ranked:
        if item.on and (item.priority >= 0 or item.age < item.min_on_s) and not overload:
            targets.add(item.entity)
            budget -= item.watts
    for item in ranked:
        if item.entity in targets or not item.on and item.age < item.min_off_s:
            continue
        if budget >= item.watts + (0 if item.on else START_MARGIN_W):
            targets.add(item.entity)
            budget -= item.watts

    desired = frozenset(targets)
    for item in reversed(running):
        if item.entity not in desired:
            return OutletPlan(desired, turn_off=item.entity,
                              reason="Uvolňuji výkon podle priorit")
    for item in ranked:
        if not item.on and item.entity in desired:
            if measured_headroom >= item.watts + START_MARGIN_W:
                return OutletPlan(desired, turn_on=item.entity, reason="Dostatek FV přebytku")
            return OutletPlan(desired, reason="Čekám na naměřenou výkonovou rezervu")
    return OutletPlan(desired, reason="Zásuvky odpovídají dostupnému výkonu a prioritám")
