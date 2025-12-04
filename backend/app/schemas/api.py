"""Pydantic schemas for API requests and responses."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


# Chat schemas
class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(..., description="User message to process")
    conversation_id: str | None = Field(
        None, description="Optional conversation ID for context"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Optional metadata for the request"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    message: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: list[dict[str, Any]] = Field(
        default_factory=list, description="Sources used for RAG response"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Optional response metadata"
    )


# Knowledge base schemas
class DocumentInput(BaseModel):
    """Input schema for adding documents to knowledge base."""

    content: str = Field(..., description="Document content")
    metadata: dict[str, Any] | None = Field(
        None, description="Optional document metadata"
    )


class DocumentResponse(BaseModel):
    """Response schema for document operations."""

    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    metadata: dict[str, Any] | None = Field(None, description="Document metadata")


class QueryRequest(BaseModel):
    """Request schema for querying knowledge base."""

    query: str = Field(..., description="Query text")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)


class QueryResponse(BaseModel):
    """Response schema for knowledge base query."""

    results: list[DocumentResponse] = Field(
        default_factory=list, description="Query results"
    )
    query: str = Field(..., description="Original query")


# Event pipeline schemas
class EventInput(BaseModel):
    """Input schema for event pipeline."""

    event_type: str = Field(..., description="Type of event")
    payload: dict[str, Any] = Field(..., description="Event payload data")
    source: str | None = Field(None, description="Event source identifier")


class EventResponse(BaseModel):
    """Response schema for event operations."""

    event_id: str = Field(..., description="Unique event ID")
    status: str = Field(..., description="Event processing status")
    timestamp: datetime = Field(
        default_factory=_utcnow, description="Event timestamp"
    )


# External API schemas
class ExternalDataRequest(BaseModel):
    """Request schema for external data ingestion."""

    source: str = Field(..., description="Data source identifier")
    data: dict[str, Any] = Field(..., description="Data payload")
    format: str = Field("json", description="Data format (json, csv, etc.)")


class ExternalDataResponse(BaseModel):
    """Response schema for external data operations."""

    request_id: str = Field(..., description="Request tracking ID")
    status: str = Field(..., description="Processing status")
    message: str | None = Field(None, description="Additional status message")


# Health check schemas
class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str = Field("healthy", description="Service health status")
    version: str = Field(..., description="Application version")
    services: dict[str, str] = Field(
        default_factory=dict, description="Individual service statuses"
    )
