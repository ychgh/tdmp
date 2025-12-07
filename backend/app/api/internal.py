"""Internal API endpoints for the chat tool."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.agents.chat_agent import get_chat_agent
from app.rag.service import get_rag_service
from app.schemas.api import (
    ChatRequest,
    ChatResponse,
    DocumentInput,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message through the AI agent.

    Args:
        request: Chat request with user message.

    Returns:
        AI agent response with sources.
    """
    logger.info("Processing chat request: %s", request.message[:50])

    try:
        agent = get_chat_agent()
        result = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            metadata=request.metadata,
        )

        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            sources=result.get("sources", []),
            metadata=result.get("metadata"),
        )

    except Exception as e:
        logger.error("Chat processing error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/documents", response_model=DocumentResponse)
async def add_document(document: DocumentInput) -> DocumentResponse:
    """Add a document to the knowledge base.

    Args:
        document: Document content and metadata.

    Returns:
        Created document with ID.
    """
    logger.info("Adding document to knowledge base")

    try:
        rag_service = get_rag_service()
        doc_id = rag_service.add_document(
            content=document.content,
            metadata=document.metadata,
        )

        return DocumentResponse(
            id=doc_id,
            content=document.content,
            metadata=document.metadata,
        )

    except Exception as e:
        logger.error("Error adding document: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest) -> QueryResponse:
    """Query the knowledge base.

    Args:
        request: Query request with search text.

    Returns:
        Query results.
    """
    logger.info("Querying knowledge base: %s", request.query[:50])

    try:
        rag_service = get_rag_service()
        results = rag_service.query(
            query_text=request.query,
            top_k=request.top_k,
        )

        return QueryResponse(
            results=[
                DocumentResponse(
                    id=r["id"],
                    content=r["content"],
                    metadata=r.get("metadata"),
                )
                for r in results
            ],
            query=request.query,
        )

    except Exception as e:
        logger.error("Query error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str) -> DocumentResponse:
    """Get a document by ID.

    Args:
        doc_id: Document ID.

    Returns:
        Document content and metadata.
    """
    logger.info("Getting document: %s", doc_id)

    try:
        rag_service = get_rag_service()
        doc = rag_service.get_document(doc_id)

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse(
            id=doc["id"],
            content=doc["content"],
            metadata=doc.get("metadata"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting document: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/documents/{doc_id}")
async def delete_document(doc_id: str) -> dict[str, Any]:
    """Delete a document from the knowledge base.

    Args:
        doc_id: Document ID to delete.

    Returns:
        Deletion confirmation.
    """
    logger.info("Deleting document: %s", doc_id)

    try:
        rag_service = get_rag_service()
        rag_service.delete_document(doc_id)

        return {"status": "deleted", "id": doc_id}

    except Exception as e:
        logger.error("Error deleting document: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def get_knowledge_stats() -> dict[str, Any]:
    """Get knowledge base statistics.

    Returns:
        Stats about the knowledge base.
    """
    try:
        rag_service = get_rag_service()
        count = rag_service.get_collection_count()

        return {
            "document_count": count,
            "status": "healthy",
        }

    except Exception as e:
        logger.error("Error getting stats: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
