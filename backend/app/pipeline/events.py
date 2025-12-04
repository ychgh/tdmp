"""Event pipeline for processing data events."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from collections import deque

logger = logging.getLogger(__name__)


class EventPipeline:
    """Event pipeline for processing and routing data events.

    In production, this would use Redis/Celery for distributed processing.
    For local development, uses an in-memory queue.
    """

    def __init__(self) -> None:
        """Initialize the event pipeline."""
        self._queue: deque[dict[str, Any]] = deque(maxlen=1000)
        self._processed: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, list[callable]] = {}
        logger.info("Event pipeline initialized")

    def register_handler(self, event_type: str, handler: callable) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Type of event to handle.
            handler: Handler function to call.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info("Registered handler for event type: %s", event_type)

    def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        source: str | None = None,
    ) -> str:
        """Publish an event to the pipeline.

        Args:
            event_type: Type of event.
            payload: Event payload data.
            source: Optional source identifier.

        Returns:
            Event ID.
        """
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }

        self._queue.append(event)
        logger.info("Published event %s of type %s", event_id, event_type)
        return event_id

    def process_next(self) -> dict[str, Any] | None:
        """Process the next event in the queue.

        Returns:
            Processed event or None if queue is empty.
        """
        if not self._queue:
            return None

        event = self._queue.popleft()
        event_type = event["event_type"]

        try:
            # Call registered handlers
            handlers = self._handlers.get(event_type, [])
            for handler in handlers:
                handler(event["payload"])

            event["status"] = "completed"
            event["processed_at"] = datetime.now(timezone.utc).isoformat()
            logger.info("Processed event %s", event["event_id"])

        except Exception as e:
            event["status"] = "failed"
            event["error"] = str(e)
            logger.error("Failed to process event %s: %s", event["event_id"], e)

        self._processed[event["event_id"]] = event
        return event

    def process_all(self) -> list[dict[str, Any]]:
        """Process all pending events.

        Returns:
            List of processed events.
        """
        processed = []
        while self._queue:
            event = self.process_next()
            if event:
                processed.append(event)
        return processed

    def get_event_status(self, event_id: str) -> dict[str, Any] | None:
        """Get the status of an event.

        Args:
            event_id: Event ID to check.

        Returns:
            Event status dict or None if not found.
        """
        # Check processed events
        if event_id in self._processed:
            return self._processed[event_id]

        # Check pending queue
        for event in self._queue:
            if event["event_id"] == event_id:
                return event

        return None

    def get_queue_size(self) -> int:
        """Get the number of pending events.

        Returns:
            Number of events in queue.
        """
        return len(self._queue)

    def get_processed_count(self) -> int:
        """Get the number of processed events.

        Returns:
            Number of processed events.
        """
        return len(self._processed)


# Singleton instance
_event_pipeline: EventPipeline | None = None


def get_event_pipeline() -> EventPipeline:
    """Get or create event pipeline singleton.

    Returns:
        EventPipeline instance.
    """
    global _event_pipeline
    if _event_pipeline is None:
        _event_pipeline = EventPipeline()
    return _event_pipeline
