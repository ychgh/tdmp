"""LangGraph-based AI agent for chat interactions."""

import logging
import uuid
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from app.core.config import get_settings
from app.rag.service import get_rag_service

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the agent graph."""

    message: str
    conversation_id: str
    context: list[dict[str, Any]]
    response: str
    sources: list[dict[str, Any]]
    metadata: dict[str, Any]


class ChatAgent:
    """LangGraph-based chat agent with RAG capabilities."""

    def __init__(self) -> None:
        """Initialize the chat agent."""
        self._settings = get_settings()
        self._rag_service = get_rag_service()
        self._graph = self._build_graph()
        logger.info("Chat agent initialized")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph.

        Returns:
            Compiled state graph.
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("retrieve", self._retrieve_context)
        workflow.add_node("generate", self._generate_response)

        # Set entry point
        workflow.set_entry_point("retrieve")

        # Add edges
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context from knowledge base.

        Args:
            state: Current agent state.

        Returns:
            Updated state with context.
        """
        logger.info("Retrieving context for: %s", state["message"][:50])

        # Query RAG service for relevant documents
        results = self._rag_service.query(state["message"], top_k=5)

        state["context"] = results
        state["sources"] = [
            {"id": r["id"], "content": r["content"][:200], "metadata": r.get("metadata", {})}
            for r in results
        ]

        logger.info("Retrieved %d context documents", len(results))
        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response based on context and message.

        Args:
            state: Current agent state.

        Returns:
            Updated state with response.
        """
        logger.info("Generating response")

        # Build context string from retrieved documents
        context_str = "\n\n".join(
            f"Document {i+1}: {doc.get('content', '')}"
            for i, doc in enumerate(state["context"])
        )

        # NOTE: This is a mock implementation for demonstration purposes.
        # In production, integrate with an LLM (e.g., OpenAI GPT-4) by:
        # 1. Creating a prompt with the user message and context
        # 2. Calling the LLM API (langchain_openai.ChatOpenAI)
        # 3. Parsing and returning the LLM response
        #
        # Example production implementation:
        #   from langchain_openai import ChatOpenAI
        #   llm = ChatOpenAI(model=settings.openai_model)
        #   prompt = f"Context:\n{context_str}\n\nQuestion: {state['message']}"
        #   response = llm.invoke(prompt)
        if context_str.strip():
            response = (
                f"Based on the available knowledge base, here's what I found:\n\n"
                f"Your query: {state['message']}\n\n"
                f"Relevant information:\n{context_str[:500]}...\n\n"
                f"I found {len(state['context'])} relevant documents."
            )
        else:
            response = (
                f"I received your message: '{state['message']}'\n\n"
                f"Currently, I don't have specific information in my knowledge base "
                f"to answer this question. Please add relevant documents to enhance "
                f"my knowledge, or rephrase your question."
            )

        state["response"] = response
        logger.info("Response generated successfully")
        return state

    async def process_message(
        self,
        message: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a chat message through the agent.

        Args:
            message: User message to process.
            conversation_id: Optional conversation ID for context.
            metadata: Optional metadata for the request.

        Returns:
            Response dict with message, conversation_id, and sources.
        """
        conv_id = conversation_id or str(uuid.uuid4())

        initial_state: AgentState = {
            "message": message,
            "conversation_id": conv_id,
            "context": [],
            "response": "",
            "sources": [],
            "metadata": metadata or {},
        }

        # Run the graph
        result = self._graph.invoke(initial_state)

        return {
            "message": result["response"],
            "conversation_id": conv_id,
            "sources": result["sources"],
            "metadata": result.get("metadata"),
        }


# Singleton instance
_chat_agent: ChatAgent | None = None


def get_chat_agent() -> ChatAgent:
    """Get or create chat agent singleton.

    Returns:
        ChatAgent instance.
    """
    global _chat_agent
    if _chat_agent is None:
        _chat_agent = ChatAgent()
    return _chat_agent
