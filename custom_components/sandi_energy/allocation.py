"""Divide a common solar budget among EV, water heating and the outlet list."""

from dataclasses import replace
from math import floor

from .outlets import plan_outlets
from .policy import MIN_A, SOLAR_RESTART_RESERVE_W, plan_ev


def allocate(data, config, outlets, boiler_demand, boiler_heating, boiler_on=False):
    observed_ev = plan_ev(data, config)
    limit = config["inverter_limit_w"]
    reserve = config["pv_reserve_w"]
    outlet_plan = plan_outlets(outlets, data.pv_w, data.eps_w, reserve, limit)
    if data.eps_w is None or data.pv_w is None:
        return observed_ev, boiler_demand, outlet_plan

    preview = not any(config[f"control_{name}"] for name in ("ev", "boiler", "outlets"))
    groups = sorted(
        (name for name in ("ev", "boiler", "outlet")
         if preview or config["control_outlets" if name == "outlet" else f"control_{name}"]),
        key=lambda name: (-config[f"{name}_priority"], name),
    )
    boiler_used = config["boiler_w"] if boiler_heating and "boiler" in groups else 0
    outlet_used = sum(item.watts for item in outlets if item.on and item.enabled) if "outlet" in groups else 0
    other_groups_w = boiler_used + outlet_used
    # EV only enters this budget if solar would be used. A mains session is separate.
    ev_used = (data.ev_w or 0) if "ev" in groups and observed_ev.mode == "solar" and data.source_solar else 0
    house_w = max(0, data.eps_w - other_groups_w - ev_used)
    remaining = min(data.pv_w - house_w - reserve, limit - house_w)
    eva = observed_ev
    allow_boiler = boiler_demand
    per_amp = 230 * config["phases"]
    eps_overloaded = data.eps_w > limit
    protected_outlets = (sum(item.watts for item in outlets if item.on and item.enabled and item.priority >= 0)
                         if "outlet" in groups and not eps_overloaded else 0)
    protected_boiler = (boiler_demand and boiler_on and "boiler" in groups
                        and config["boiler_priority"] >= 0 and data.eps_w <= min(4000, limit))
    protected_ev = ("ev" in groups and observed_ev.mode == "solar" and data.session and data.source_solar
                    and config["ev_priority"] >= 0 and observed_ev.available_w is not None
                    and max(0, data.eps_w - ev_used) + MIN_A * per_amp <= limit)
    remaining -= protected_outlets + (config["boiler_w"] if protected_boiler else 0)
    if protected_ev:
        remaining -= MIN_A * per_amp

    for name in groups:
        if name == "ev" and observed_ev.mode == "solar":
            baseline = replace(data, eps_w=max(0, data.eps_w - other_groups_w))
            potential = plan_ev(baseline, config)
            if protected_ev:
                additional = max(0, min((potential.amps or MIN_A) - MIN_A, floor(remaining / per_amp)))
                eva = replace(potential, amps=MIN_A + additional,
                              reason="Běžící nabíjení je chráněné prioritou" if not additional else potential.reason)
                remaining -= additional * per_amp
            elif potential.amps:
                start_margin = 0 if data.session and data.source_solar else SOLAR_RESTART_RESERVE_W
                ceiling = min(potential.amps, floor(remaining / per_amp))
                if ceiling >= MIN_A and remaining >= MIN_A * per_amp + start_margin:
                    eva = replace(potential, amps=ceiling, available_w=remaining)
                    remaining -= ceiling * per_amp
                else:
                    eva = replace(potential, amps=0, available_w=remaining,
                                  reason="Výkon je vyhrazen vyšší prioritě")
            else:
                eva = potential
        elif name == "boiler" and boiler_demand:
            allow_boiler = protected_boiler or remaining >= config["boiler_w"]
            if allow_boiler and not protected_boiler:
                remaining -= config["boiler_w"]
        elif name == "outlet":
            outlet_plan = plan_outlets(outlets, data.pv_w, data.eps_w, reserve, limit, remaining + protected_outlets)
            remaining -= sum(item.watts for item in outlets if item.entity in outlet_plan.targets) - protected_outlets
    return eva, allow_boiler, outlet_plan
