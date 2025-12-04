"""RAG service using Chroma vector database."""

import hashlib
import logging
import os
import uuid
from typing import Any

import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SimpleEmbeddingFunction(EmbeddingFunction):
    """A simple embedding function that creates deterministic embeddings.

    This is used for testing when network access is not available.
    In production, you would use a proper embedding model.
    """

    def __init__(self) -> None:
        """Initialize the embedding function."""
        pass

    @staticmethod
    def name() -> str:
        """Return the name of the embedding function."""
        return "simple_hash_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        """Create embeddings for documents.

        Args:
            input: List of document texts.

        Returns:
            List of embedding vectors.
        """
        embeddings = []
        for doc in input:
            # Create a deterministic hash-based embedding
            doc_hash = hashlib.sha256(doc.encode()).digest()
            # Convert to a 384-dimensional vector (to match mini-lm size)
            embedding = []
            for i in range(0, min(len(doc_hash), 32), 1):
                val = doc_hash[i] / 255.0 - 0.5  # Normalize to [-0.5, 0.5]
                embedding.append(val)
            # Pad to 384 dimensions with deterministic values
            while len(embedding) < 384:
                idx = len(embedding)
                val = ((doc_hash[idx % 32] + idx) % 256) / 255.0 - 0.5
                embedding.append(val)
            embeddings.append(embedding)
        return embeddings


class RAGService:
    """Service for RAG operations using Chroma vector database."""

    def __init__(self, use_ephemeral: bool = False) -> None:
        """Initialize RAG service with Chroma client.

        Args:
            use_ephemeral: If True, use ephemeral in-memory storage.
                          Useful for testing.
        """
        settings = get_settings()

        # Use ephemeral client for testing or if explicitly requested
        is_testing = use_ephemeral or os.environ.get("TESTING", "").lower() == "true"
        if is_testing:
            self._client = chromadb.EphemeralClient()
        else:
            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory
            )

        # Use simple embedding function for testing (no network required)
        # In production, use proper embedding models like OpenAI or sentence-transformers
        embedding_function = SimpleEmbeddingFunction() if is_testing else None

        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_function,
        )
        logger.info(
            "RAG service initialized with collection: %s",
            settings.chroma_collection_name,
        )

    def add_document(
        self, content: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """Add a document to the knowledge base.

        Args:
            content: Document content to add.
            metadata: Optional metadata for the document.

        Returns:
            Document ID.
        """
        doc_id = str(uuid.uuid4())
        self._collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
        logger.info("Added document with ID: %s", doc_id)
        return doc_id

    def add_documents(
        self, contents: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[str]:
        """Add multiple documents to the knowledge base.

        Args:
            contents: List of document contents.
            metadatas: Optional list of metadata dicts.

        Returns:
            List of document IDs.
        """
        doc_ids = [str(uuid.uuid4()) for _ in contents]
        self._collection.add(
            documents=contents,
            metadatas=metadatas or [{} for _ in contents],
            ids=doc_ids,
        )
        logger.info("Added %d documents", len(doc_ids))
        return doc_ids

    def query(
        self, query_text: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Query the knowledge base.

        Args:
            query_text: Query string.
            top_k: Number of results to return.

        Returns:
            List of matching documents with metadata.
        """
        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        documents = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = {
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                }
                if results.get("distances"):
                    doc["distance"] = results["distances"][0][i]
                documents.append(doc)

        logger.info("Query returned %d results", len(documents))
        return documents

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base.

        Args:
            doc_id: Document ID to delete.

        Returns:
            True if successful.
        """
        self._collection.delete(ids=[doc_id])
        logger.info("Deleted document with ID: %s", doc_id)
        return True

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID.

        Args:
            doc_id: Document ID.

        Returns:
            Document dict or None if not found.
        """
        results = self._collection.get(ids=[doc_id])
        if results and results["ids"]:
            return {
                "id": results["ids"][0],
                "content": results["documents"][0] if results["documents"] else "",
                "metadata": results["metadatas"][0] if results["metadatas"] else {},
            }
        return None

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection.

        Returns:
            Number of documents.
        """
        return self._collection.count()


# Singleton instance
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton.

    Returns:
        RAGService instance.
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
