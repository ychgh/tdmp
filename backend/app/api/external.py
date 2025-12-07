"""External API endpoints for 3rd party integration."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from app.pipeline.events import get_event_pipeline
from app.rag.service import get_rag_service
from app.schemas.api import (
    EventInput,
    EventResponse,
    ExternalDataRequest,
    ExternalDataResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/external", tags=["external"])


@router.post("/data/ingest", response_model=ExternalDataResponse)
async def ingest_data(request: ExternalDataRequest) -> ExternalDataResponse:
    """Ingest data from external sources.

    This endpoint accepts data from 3rd party integrations and
    processes it through the event pipeline.

    Args:
        request: External data request.

    Returns:
        Data ingestion response with tracking ID.
    """
    logger.info("Ingesting data from source: %s", request.source)

    try:
        pipeline = get_event_pipeline()

        # Publish event to pipeline
        event_id = pipeline.publish(
            event_type="data_ingestion",
            payload={
                "source": request.source,
                "data": request.data,
                "format": request.format,
            },
            source=request.source,
        )

        return ExternalDataResponse(
            request_id=event_id,
            status="accepted",
            message="Data ingestion request accepted and queued for processing",
        )

    except Exception as e:
        logger.error("Data ingestion error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events", response_model=EventResponse)
async def publish_event(event: EventInput) -> EventResponse:
    """Publish an event to the event pipeline.

    Args:
        event: Event to publish.

    Returns:
        Event response with ID and status.
    """
    logger.info("Publishing event of type: %s", event.event_type)

    try:
        pipeline = get_event_pipeline()

        event_id = pipeline.publish(
            event_type=event.event_type,
            payload=event.payload,
            source=event.source,
        )

        return EventResponse(
            event_id=event_id,
            status="published",
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error("Event publish error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}")
async def get_event_status(event_id: str) -> dict[str, Any]:
    """Get the status of a published event.

    Args:
        event_id: Event ID to check.

    Returns:
        Event status information.
    """
    logger.info("Getting event status: %s", event_id)

    try:
        pipeline = get_event_pipeline()
        event = pipeline.get_event_status(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting event status: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/bulk")
async def bulk_import_documents(
    documents: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bulk import documents to the knowledge base.

    Args:
        documents: List of documents with content and metadata.

    Returns:
        Import results with document IDs.
    """
    # Validate document count to prevent memory exhaustion
    MAX_BULK_DOCUMENTS = 100
    if len(documents) > MAX_BULK_DOCUMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot import more than {MAX_BULK_DOCUMENTS} documents at once"
        )

    logger.info("Bulk importing %d documents", len(documents))

    try:
        rag_service = get_rag_service()

        contents = [doc.get("content", "") for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        doc_ids = rag_service.add_documents(
            contents=contents,
            metadatas=metadatas,
        )

        return {
            "status": "success",
            "imported_count": len(doc_ids),
            "document_ids": doc_ids,
        }

    except Exception as e:
        logger.error("Bulk import error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/stats")
async def get_pipeline_stats() -> dict[str, Any]:
    """Get event pipeline statistics.

    Returns:
        Pipeline statistics.
    """
    try:
        pipeline = get_event_pipeline()

        return {
            "pending_events": pipeline.get_queue_size(),
            "processed_events": pipeline.get_processed_count(),
            "status": "healthy",
        }

    except Exception as e:
        logger.error("Error getting pipeline stats: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def webhook_handler(payload: dict[str, Any]) -> dict[str, Any]:
    """Generic webhook handler for external integrations.

    Args:
        payload: Webhook payload.

    Returns:
        Webhook acknowledgment.
    """
    logger.info("Received webhook: %s", payload.get("event_type", "unknown"))

    try:
        pipeline = get_event_pipeline()

        # Extract event type or use default
        event_type = payload.get("event_type", "webhook")

        event_id = pipeline.publish(
            event_type=event_type,
            payload=payload,
            source="webhook",
        )

        return {
            "status": "received",
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error("Webhook processing error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
