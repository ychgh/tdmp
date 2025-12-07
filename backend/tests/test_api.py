"""Tests for the FastAPI application."""

import os

# Set testing environment before importing app
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import rag, agents


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    # Reset RAG service singleton
    rag.service._rag_service = None
    # Reset chat agent singleton
    agents.chat_agent._chat_agent = None
    yield
    # Cleanup after test
    rag.service._rag_service = None
    agents.chat_agent._chat_agent = None


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data

    def test_health_endpoint(self, client):
        """Test health endpoint returns health status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestInternalAPIEndpoints:
    """Tests for internal API endpoints."""

    def test_chat_endpoint(self, client):
        """Test chat endpoint."""
        response = client.post(
            "/api/v1/internal/chat",
            json={"message": "Hello, how can you help me?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "conversation_id" in data

    def test_add_document(self, client):
        """Test adding a document to knowledge base."""
        response = client.post(
            "/api/v1/internal/knowledge/documents",
            json={
                "content": "This is a test document about Python programming.",
                "metadata": {"type": "test", "language": "python"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == "This is a test document about Python programming."

    def test_query_knowledge(self, client):
        """Test querying the knowledge base."""
        # First add a document
        client.post(
            "/api/v1/internal/knowledge/documents",
            json={"content": "Python is a programming language."},
        )

        # Then query
        response = client.post(
            "/api/v1/internal/knowledge/query",
            json={"query": "programming language", "top_k": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data

    def test_get_knowledge_stats(self, client):
        """Test getting knowledge base stats."""
        response = client.get("/api/v1/internal/knowledge/stats")
        assert response.status_code == 200
        data = response.json()
        assert "document_count" in data
        assert "status" in data


class TestExternalAPIEndpoints:
    """Tests for external API endpoints."""

    def test_ingest_data(self, client):
        """Test data ingestion endpoint."""
        response = client.post(
            "/api/v1/external/data/ingest",
            json={
                "source": "test-source",
                "data": {"key": "value"},
                "format": "json",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "request_id" in data

    def test_publish_event(self, client):
        """Test event publishing endpoint."""
        response = client.post(
            "/api/v1/external/events",
            json={
                "event_type": "test_event",
                "payload": {"test": "data"},
                "source": "test-source",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
        assert data["status"] == "published"

    def test_bulk_import_documents(self, client):
        """Test bulk document import."""
        response = client.post(
            "/api/v1/external/documents/bulk",
            json=[
                {"content": "Document 1", "metadata": {"type": "test"}},
                {"content": "Document 2", "metadata": {"type": "test"}},
            ],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["imported_count"] == 2

    def test_bulk_import_documents_limit(self, client):
        """Test bulk document import rejects more than 100 documents."""
        # Create 101 documents
        documents = [
            {"content": f"Document {i}", "metadata": {"type": "test"}}
            for i in range(101)
        ]
        response = client.post(
            "/api/v1/external/documents/bulk",
            json=documents,
        )
        assert response.status_code == 400
        data = response.json()
        assert "Cannot import more than 100 documents" in data["detail"]

    def test_webhook_handler(self, client):
        """Test webhook handler."""
        response = client.post(
            "/api/v1/external/webhook",
            json={"event_type": "test", "data": {"key": "value"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert "event_id" in data

    def test_get_pipeline_stats(self, client):
        """Test getting pipeline stats."""
        response = client.get("/api/v1/external/pipeline/stats")
        assert response.status_code == 200
        data = response.json()
        assert "pending_events" in data
        assert "processed_events" in data
