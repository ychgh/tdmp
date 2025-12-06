/**
 * API client for communicating with the backend.
 */

import type {
  ChatRequest,
  ChatResponse,
  DocumentInput,
  DocumentResponse,
  QueryRequest,
  QueryResponse,
  HealthCheck,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Make an API request.
 */
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Chat API functions.
 */
export const chatApi = {
  /**
   * Send a chat message to the AI agent.
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    return apiRequest<ChatResponse>("/api/v1/internal/chat", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },
};

/**
 * Knowledge base API functions.
 */
export const knowledgeApi = {
  /**
   * Add a document to the knowledge base.
   */
  addDocument: async (document: DocumentInput): Promise<DocumentResponse> => {
    return apiRequest<DocumentResponse>("/api/v1/internal/knowledge/documents", {
      method: "POST",
      body: JSON.stringify(document),
    });
  },

  /**
   * Query the knowledge base.
   */
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    return apiRequest<QueryResponse>("/api/v1/internal/knowledge/query", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * Get a document by ID.
   */
  getDocument: async (id: string): Promise<DocumentResponse> => {
    return apiRequest<DocumentResponse>(
      `/api/v1/internal/knowledge/documents/${id}`
    );
  },

  /**
   * Delete a document.
   */
  deleteDocument: async (id: string): Promise<{ status: string; id: string }> => {
    return apiRequest<{ status: string; id: string }>(
      `/api/v1/internal/knowledge/documents/${id}`,
      { method: "DELETE" }
    );
  },

  /**
   * Get knowledge base stats.
   */
  getStats: async (): Promise<{ document_count: number; status: string }> => {
    return apiRequest<{ document_count: number; status: string }>(
      "/api/v1/internal/knowledge/stats"
    );
  },
};

/**
 * Health check API functions.
 */
export const healthApi = {
  /**
   * Check API health.
   */
  check: async (): Promise<HealthCheck> => {
    return apiRequest<HealthCheck>("/health");
  },
};
