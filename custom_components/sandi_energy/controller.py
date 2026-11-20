"""Read Home Assistant entities and serialize changes across all actuators."""

import asyncio
from datetime import timedelta
from math import isclose, isfinite
from time import monotonic

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.util import dt as dt_util

from .allocation import allocate
from .const import CONTROL_DEFAULTS, ENTITY_DOMAINS
from .manual import manual_service
from .outlets import POWER_UNITS, START_STABLE_SECONDS, Outlet
from .policy import (
    EVInput, IDLE_STATUSES, MIN_A, SOLAR_INCREASE_SECONDS,
    SOURCE_IDLE_SECONDS, SOURCE_SETTLE_SECONDS, boiler_preset, plan_ev,
)


class EnergyController:
    def __init__(self, hass, entry, audit):
        self.hass = hass
        self.entry = entry
        self.audit = audit
        self.entities = {role: entry.data.get(role) for role in ENTITY_DOMAINS}
        self.config = {**CONTROL_DEFAULTS, **entry.options}
        self.outlet_settings = self._allowed_outlets(entry.options.get("outlets", []))
        self.listeners = []
        self.diagnostics = {"ev": {}, "boiler": {}, "outlets": {}}
        self._unsubscribe_states = None
        self._unsubscribe_tick = None
        self._outlet_generation = 0
        self._task = None
        self._pending = False
        self._running = False
        self._attempts = {}
        self._errors = {}
        self._idle_since = None
        self._source_pending_until = 0
        self._solar_ready_since = None
        self._increase_since = None
        self._restore_mode = None
        self._restore_cause = None
        self._boiler_pending = None
        self._boiler_recovery_since = None
        self._outlet_ready = None
        self._outlet_ready_since = 0
        self._outlet_last_command = float("-inf")
        self._last_power_command = float("-inf")
        self.action_lock = asyncio.Lock()

    @callback
    def start(self, _hass):
        self._running = True
        self._watch_states()
        self._unsubscribe_tick = async_track_time_interval(self.hass, self._request, timedelta(seconds=5))
        self._request()

    def _allowed_outlets(self, outlets):
        reserved = {self.entities["source"], self.entities["session"]}
        return [item for item in outlets if item["entity"].startswith("switch.") and item["entity"] not in reserved]

    @callback
    def _watch_states(self):
        if self._unsubscribe_states is not None:
            self._unsubscribe_states()
        watched = {entity for entity in self.entities.values() if entity}
        watched.update(item["entity"] for item in self.outlet_settings)
        watched.update(item["power_sensor"] for item in self.outlet_settings if item.get("power_sensor"))
        self._unsubscribe_states = async_track_state_change_event(self.hass, watched, self._request)

    @callback
    def apply_outlets(self, outlets):
        """Apply panel changes without restarting EV or boiler control."""
        self.outlet_settings = self._allowed_outlets(outlets)
        self._outlet_generation += 1
        self._outlet_ready = None
        if self._running:
            self._watch_states()
        self._request()

    @callback
    def apply_entities(self, data, role):
        """Rebind state listeners while holding the actuator lock."""
        self.entities = {key: data.get(key) for key in ENTITY_DOMAINS}
        self._outlet_ready = None
        if role != "boiler":
            self._idle_since = None
            self._solar_ready_since = None
            self._increase_since = None
        if role in ("source", "session", "ev_power", "ev_status"):
            self._source_pending_until = max(self._source_pending_until, monotonic() + SOURCE_SETTLE_SECONDS)
        if role == "boiler":
            self._restore_mode = None
            self._restore_cause = None
            self._boiler_pending = None
            self._boiler_recovery_since = None
        self._attempts = {attempt: now for attempt, now in self._attempts.items() if attempt[0] != role}
        self._errors.pop(role, None)
        self.apply_outlets(self.entry.options.get("outlets", []))

    @callback
    def apply_controls(self, settings):
        previous = self.config
        self.config = {**previous, **settings}
        self._solar_ready_since = None
        self._increase_since = None
        self._outlet_ready = None
        if previous["control_boiler"] != settings["control_boiler"]:
            self._restore_mode = None
            self._boiler_pending = None
            self._boiler_recovery_since = None
        self._request()

    async def stop(self):
        self._running = False
        if self._unsubscribe_states is not None:
            self._unsubscribe_states()
            self._unsubscribe_states = None
        if self._unsubscribe_tick is not None:
            self._unsubscribe_tick()
            self._unsubscribe_tick = None
        if self._task is not None:
            # Drain the in-flight service before Home Assistant reloads the entry.
            await asyncio.gather(self._task, return_exceptions=True)
        async with self.action_lock:
            pass

    @callback
    def _request(self, _event_or_time=None):
        if not self._running:
            return
        power = self._power("ev_power")
        if power is None or power >= 50 or self._flag("session") is not False:
            self._idle_since = None
        self._pending = True
        if self._task is None or self._task.done():
            self._task = self.entry.async_create_background_task(
                self.hass, self._drain(), "SANDI energy regulation"
            )

    async def _drain(self):
        while self._running and self._pending:
            self._pending = False
            async with self.action_lock:
                if self._running:
                    await self._evaluate()

    def _state(self, key):
        entity = self.entities.get(key)
        return self.hass.states.get(entity) if entity else None

    def _value(self, key):
        state = self._state(key)
        if state and state.state not in {"unknown", "unavailable"}:
            return state.state
        return None

    def _flag(self, key):
        return {"on": True, "off": False}.get(self._value(key))

    def _age(self, key):
        state = self._state(key)
        return (dt_util.utcnow() - state.last_changed).total_seconds() if state else 0

    def _numeric(self, key):
        try:
            value = float(self._value(key))
        except (ValueError, TypeError):
            return None
        return value if isfinite(value) else None

    def _power(self, key):
        return self._watts(self._state(key))

    def _watts(self, state):
        if state is None:
            return None
        try:
            value = float(state.state)
        except (ValueError, TypeError):
            return None
        if not isfinite(value) or value < 0:
            return None
        reported = getattr(state, "last_reported", state.last_updated)
        if (dt_util.utcnow() - reported).total_seconds() > self.config["power_max_age_s"]:
            return None
        factor = POWER_UNITS.get(state.attributes.get("unit_of_measurement"))
        return value * factor if factor is not None else None

    def _eps(self):
        powers = (self._power("eps"), self._power("overload"))
        return max((power for power in powers if power is not None), default=None)

    def _publish(self, key, values):
        if self.diagnostics[key] != values:
            self.diagnostics[key] = values
            for listener in tuple(self.listeners):
                listener()

    async def _call(self, key, service, *, cooldown=8, entity=None, context=None, **data):
        if not self._running:
            return False
        entity_id = entity or self.entities[key]
        if not entity_id:
            return False
        attempt = (key, service, tuple(data.items()))
        now = monotonic()
        if now - self._attempts.get(attempt, float("-inf")) < cooldown:
            return False
        self._attempts[attempt] = now
        self._last_power_command = now
        try:
            async with asyncio.timeout(8):
                await self.hass.services.async_call(
                    entity_id.partition(".")[0], service,
                    {"entity_id": entity_id, **data}, blocking=True, context=context,
                )
        except (HomeAssistantError, TimeoutError) as err:
            self._errors[key] = f"{service}: {err or type(err).__name__}"
            self.audit.record("manual" if context else "automatic", service, entity_id,
                              details=data, error=str(err) or type(err).__name__)
            return False
        self._errors.pop(key, None)
        self.audit.record("manual" if context else "automatic", service, entity_id, details=data)
        return True

    async def run_manual(self, command, value, context, *, mapping=None):
        """Validate and dispatch one user action using the same service path."""
        async with self.action_lock:
            if not self._running:
                raise ValueError("Regulátor se ještě nenačetl.")
            if mapping is not None and mapping != self.entities:
                raise ValueError("Přiřazení entit se změnilo. Zkontroluj aktuální zařízení a povel zopakuj.")
            key, service, data = manual_service(self, command, value)
            if not await self._call(key, service, context=context, **data):
                raise ValueError(self._errors.get(key, "Povel už byl odeslán. Zkontroluj stav zařízení."))

    async def _evaluate(self):
        outlet_generation = self._outlet_generation
        source = self._flag("source")
        data = EVInput(
            solar=self._flag("solar_enabled"), night=self._flag("night_enabled"),
            tariff=self._flag("tariff"), tariff_age=self._age("tariff"),
            connected=self._flag("connected"), status=self._value("ev_status"),
            session=self._flag("session"),
            source_solar=(source == self.config["sonoff_on_is_solar"] if source is not None else None),
            pv_w=self._power("pv"), eps_w=self._eps(),
            ev_w=self._power("ev_power"),
            soc=self._numeric("soc"),
        )
        outlets = self._outlets()
        thermostat = self._state("boiler")
        preset = boiler_preset(dt_util.now().hour, self._numeric("eta"))
        heating = bool(thermostat and self._value("boiler") not in {None, "off"}
                       and thermostat.attributes.get("hvac_action") == "heating")
        if preset is None and thermostat:
            requested_preset = thermostat.attributes.get("preset_mode")
        else:
            requested_preset = preset
        boiler_demand = (requested_preset in {"activity", "eco"}
                         and (self._value("boiler") not in {None, "off"}
                              or self._restore_mode is not None or self._boiler_pending is not None))
        plan, boiler_allowed, outlet_plan = allocate(
            data, self.config, outlets, boiler_demand, heating and boiler_demand,
            self._value("boiler") not in {None, "off"},
        )
        action, reason = self._ev_action(data, plan)
        if action and plan.mode == "solar" and self._adds_ev_load(action):
            observed = plan_ev(data, self.config)
            requested = action[2].get("value", self._numeric("current") or MIN_A)
            if (not observed.amps or observed.amps < requested
                    or monotonic() - self._last_power_command < 10):
                action, reason = None, "Čekám na potvrzení rezervy po změně odběru"
        if action and self.config["control_ev"]:
            key, service, fields = action
            if key != "source" or self.config["control_source"]:
                if key == "source":
                    self._source_pending_until = monotonic() + SOURCE_SETTLE_SECONDS
                    self._idle_since = None
                await self._call(key, service, **fields)
        self._publish("ev", {
            "state": plan.mode,
            "reason": reason,
            "control_enabled": self.config["control_ev"],
            "source_control_enabled": self.config["control_source"],
            "actual_source": {True: "FVE", False: "síť"}.get(data.source_solar),
            "target_source": {True: "FVE", False: "síť"}.get(plan.source_solar),
            "target_current_a": plan.amps,
            "current_setpoint_a": self._numeric("current"),
            "pv_w": data.pv_w,
            "eps_w": data.eps_w,
            "eps_limit_w": self.config["inverter_limit_w"],
            "ev_w": data.ev_w,
            "battery_soc": data.soc,
            "available_w": round(plan.available_w) if plan.available_w is not None else None,
            "last_error": next((self._errors[k] for k in ("session", "current", "source")
                                if k in self._errors), None),
        })
        await self._evaluate_boiler(boiler_demand, boiler_allowed, preset)
        if outlet_generation == self._outlet_generation:
            await self._evaluate_outlets(outlets, outlet_plan)

    def _adds_ev_load(self, action):
        key, service, fields = action
        return ((key == "session" and service == "turn_on")
                or (key == "current" and fields["value"] > (self._numeric("current") or 0)))

    def _outlets(self):
        now = dt_util.utcnow()
        outlets = []
        for item in self.outlet_settings:
            state = self.hass.states.get(item["entity"])
            on = {"on": True, "off": False}.get(state.state) if state else None
            age = (now - state.last_changed).total_seconds() if state else 0
            meter = item.get("power_sensor")
            meter_state = self.hass.states.get(meter) if meter else None
            measured = self._watts(meter_state)
            if on and measured is not None and getattr(meter_state, "last_reported", meter_state.last_updated) < state.last_changed:
                measured = None
            outlets.append(Outlet(**item, on=on, age=age, measured_w=measured))
        return sorted(outlets, key=lambda item: (-item.priority, item.entity))

    async def _evaluate_outlets(self, outlets, plan):
        now = monotonic()
        reason = plan.reason
        if plan.turn_on != self._outlet_ready:
            self._outlet_ready = plan.turn_on
            self._outlet_ready_since = now
        if plan.turn_on and (now - self._outlet_ready_since < START_STABLE_SECONDS
                            or now - self._last_power_command < 15):
            reason = "Čekám na stabilní přebytek pro zapnutí zásuvky"
            entity, service = None, None
        elif plan.turn_off:
            entity, service = plan.turn_off, "turn_off"
        else:
            entity, service = plan.turn_on, "turn_on"
        control = self.config["control_outlets"]
        if control and entity and now - self._outlet_last_command >= 8:
            self._outlet_last_command = now
            await self._call(entity, service, entity=entity)

        self._publish("outlets", {
            "state": sum(item.on is True for item in outlets),
            "control_enabled": control,
            "reason": reason if outlets else "V nastavení přidej první zásuvku",
            "ev_priority": self.config["ev_priority"],
            "boiler_priority": self.config["boiler_priority"],
            "outlets": [{
                "entity": item.entity, "priority": item.priority, "watts": item.watts,
                "power_sensor": item.power_sensor, "measured_w": item.measured_w,
                "enabled": item.enabled, "on": item.on, "target_on": item.entity in plan.targets,
                "error": self._errors.get(item.entity),
            } for item in outlets],
        })

    def _ev_action(self, data, plan):
        now = monotonic()
        idle = (data.session is False and data.status in IDLE_STATUSES
                and data.ev_w is not None and data.ev_w < 50)
        self._idle_since = (self._idle_since or now) if idle else None
        if plan.mode == "solar" and plan.amps and not data.session:
            self._solar_ready_since = self._solar_ready_since or now
        else:
            self._solar_ready_since = None

        if plan.amps is None:
            self._increase_since = None
            return None, plan.reason

        switching = plan.source_solar is not None and data.source_solar != plan.source_solar
        if plan.amps == 0 or switching:
            self._increase_since = None
            if data.session is True or data.status == "charging":
                return ("session", "turn_off", {}), (
                    "Ukončuji relaci před změnou zdroje" if switching else plan.reason
                )
        if switching:
            if data.source_solar is None:
                return None, "Poloha ATS přepínače není dostupná"
            if not self.config["control_source"]:
                return None, "Čekám na změnu zdroje ATS přepínačem"
            if (self._idle_since is None or now - self._idle_since < SOURCE_IDLE_SECONDS
                    or self._age("session") < SOURCE_IDLE_SECONDS
                    or self._age("ev_status") < SOURCE_IDLE_SECONDS
                    or now < self._source_pending_until):
                return None, "Čekám na ukončenou relaci a odběr pod 50 W"
            service = "turn_on" if plan.source_solar == self.config["sonoff_on_is_solar"] else "turn_off"
            return ("source", service, {}), "Přepínám zdroj nabíječky"
        if plan.amps == 0:
            return None, plan.reason

        if (data.session is None or now < self._source_pending_until
                or self._age("source") < SOURCE_SETTLE_SECONDS):
            return None, "Čekám na potvrzení a ustálení zdroje"
        if data.session is False and data.status == "charging":
            return ("session", "turn_off", {}), "Stav nabíječky a relace si odporují"

        current = self._numeric("current")
        target = self._supported_current(plan.amps)
        if current is None or target is None:
            if data.session or data.status == "charging":
                return ("session", "turn_off", {}), "Nabíječka nemá platný setpoint proudu"
            return None, "Nabíječka nemá platný setpoint proudu"
        if self._solar_ready_since is not None and now - self._solar_ready_since < 30:
            return None, "Ověřuji FV přebytek po dobu 30 sekund"
        if not data.session:
            self._increase_since = None
            target = self._supported_current(MIN_A) if plan.mode == "solar" else target
            if target is None:
                return None, "Solární start při 6 A není podporován"
            if not isclose(current, target):
                return ("current", "set_value", {"value": target}), "Nastavuji startovací proud"
            return ("session", "turn_on", {}), plan.reason
        if current < target and plan.mode == "solar":
            self._increase_since = self._increase_since or now
            if now - self._increase_since < SOLAR_INCREASE_SECONDS:
                return None, "Čekám na stabilní přebytek před zvýšením proudu"
            target = self._supported_current(min(target, current + 1))
            if target is None or target <= current:
                return None, "Další krok proudu není podporován"
        if not isclose(current, target):
            self._increase_since = None
            return ("current", "set_value", {"value": target}), plan.reason
        self._increase_since = None
        return None, plan.reason

    def _supported_current(self, requested):
        state = self._state("current")
        if state is None:
            return None
        try:
            low, high, step = (float(state.attributes[key]) for key in ("min", "max", "step"))
        except (KeyError, ValueError, TypeError):
            return None
        if not all(isfinite(value) for value in (low, high, step)) or step <= 0:
            return None
        value = min(requested, high)
        if value < max(MIN_A, low):
            return None
        steps = int((value - low) / step + 1e-8)
        value = round(low + steps * step, 6)
        return value if value >= MIN_A else None

    async def _evaluate_boiler(self, demand, allowed, preset):
        mode = self._value("boiler")
        overload_w = self._eps()
        pv = self._power("pv")
        overload = overload_w is not None and overload_w > min(4000, self.config["inverter_limit_w"])
        blocked = overload or demand and not allowed
        actual_headroom = (min(pv - overload_w - self.config["pv_reserve_w"],
                               self.config["inverter_limit_w"] - overload_w)
                           if None not in (pv, overload_w) else None)
        reason = "Časový režim podle ETA baterie"
        now = monotonic()
        if self._boiler_pending:
            previous_mode, cause, expiry = self._boiler_pending
            if mode == "off" and now <= expiry:
                self._restore_mode = previous_mode
                self._restore_cause = cause
                self._boiler_pending = None
            elif now > expiry:
                self._boiler_pending = None
        if mode is not None and mode != "off":
            self._restore_mode = None
            self._restore_cause = None
        ready_to_recover = (overload_w is not None and not overload
                            and (self._restore_cause != "overload" or overload_w < 1500)
                            and (not demand or (actual_headroom is not None
                                                and actual_headroom >= self.config["boiler_w"])))
        if blocked or not ready_to_recover or not self._restore_mode:
            self._boiler_recovery_since = None
        else:
            self._boiler_recovery_since = self._boiler_recovery_since or now

        control = self.config["control_boiler"] and self._running
        if mode is None:
            reason = "Termostat je nedostupný"
        elif blocked:
            reason = "Přetížení EPS" if overload else "Výkon je vyhrazen vyšší prioritě"
            if control and mode != "off" and self._boiler_pending is None:
                if await self._call("boiler", "turn_off"):
                    self._boiler_pending = (mode, "overload" if overload else "priority", now + 30)
        elif mode == "off":
            reason = "Termostat zůstává vypnutý"
            if self._boiler_recovery_since is not None:
                reason = "Čekám na pět minut nízkého odběru"
                if (control and now - self._boiler_recovery_since >= 300
                        and now - self._last_power_command >= 15):
                    state = self._state("boiler")
                    if self._restore_mode in state.attributes.get("hvac_modes", []):
                        await self._call("boiler", "set_hvac_mode", hvac_mode=self._restore_mode)
        elif preset:
            state = self._state("boiler")
            if preset not in state.attributes.get("preset_modes", []):
                reason = "Termostat nenabízí požadovaný preset"
            elif (preset in {"activity", "eco"} and preset != state.attributes.get("preset_mode")
                  and state.attributes.get("hvac_action") != "heating"
                  and (actual_headroom is None or actual_headroom < self.config["boiler_w"]
                       or now - self._last_power_command < 15)):
                reason = "Čekám na potvrzenou rezervu pro bojler"
            elif control and preset != state.attributes.get("preset_mode"):
                await self._call("boiler", "set_preset_mode", preset_mode=preset)
        else:
            reason = "ETA baterie není dostupné"

        self._publish("boiler", {
            "state": "blocked" if blocked else mode or "unknown",
            "reason": reason,
            "control_enabled": self.config["control_boiler"],
            "eps_active_w": overload_w,
            "target_preset": preset,
            "last_error": self._errors.get("boiler"),
        })
