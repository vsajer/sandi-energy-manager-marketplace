"""Persist recent user actions and actuator commands locally."""

from datetime import UTC, datetime

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import DOMAIN

HISTORY_LIMIT = 300


class AuditLog:
    def __init__(self, hass, entry_id):
        self.hass = hass
        self.signal = f"{DOMAIN}_audit_{entry_id}"
        self.store = Store(hass, 1, f"{DOMAIN}.audit.{entry_id}", private=True)
        self.records = []
        self.dirty = False

    async def load(self):
        self.records = (await self.store.async_load() or {}).get("records", [])[:HISTORY_LIMIT]

    async def flush(self):
        if self.dirty:
            await self.store.async_save(self._snapshot())
            self.dirty = False

    def _snapshot(self):
        return {"records": list(self.records)}

    def record(self, origin, action, entity=None, *, details=None, error=None):
        record = {
            "time": datetime.now(UTC).isoformat(),
            "origin": origin,
            "action": action,
            "entity": entity,
            "details": details,
            "error": error,
        }
        self.records.insert(0, record)
        del self.records[HISTORY_LIMIT:]
        self.dirty = True
        self.store.async_delay_save(self._snapshot, 5)
        async_dispatcher_send(self.hass, self.signal, {"record": record})
