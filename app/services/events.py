import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.config import get_settings


def _json_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Tipo nao serializavel: {type(value)!r}")


class EventPublisher:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._producer = None

        if self.settings.kafka_enabled:
            from confluent_kafka import Producer

            self._producer = Producer({"bootstrap.servers": self.settings.kafka_bootstrap_servers})

    def publish(self, event_type: str, payload: dict[str, Any], key: str, correlation_id: str | None = None) -> None:
        event = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "eventVersion": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self.settings.app_name,
            "correlationId": correlation_id or str(uuid.uuid4()),
            "payload": payload,
        }

        if not self._producer:
            return

        self._producer.produce(
            self.settings.kafka_topic_fornecimentos,
            key=key,
            value=json.dumps(event, default=_json_default).encode("utf-8"),
        )
        self._producer.flush()


publisher = EventPublisher()
