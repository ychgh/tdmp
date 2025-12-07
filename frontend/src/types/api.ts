/**
 * API types for the chat interface.
 */

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export interface Source {
  id: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  metadata?: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  sources: Source[];
  metadata?: Record<string, unknown>;
}

export interface DocumentInput {
  content: string;
  metadata?: Record<string, unknown>;
}

export interface DocumentResponse {
  id: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface QueryResponse {
  results: DocumentResponse[];
  query: string;
}

export interface HealthCheck {
  status: string;
  version: string;
  services: Record<string, string>;
}
