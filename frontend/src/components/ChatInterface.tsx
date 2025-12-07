"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { chatApi } from "@/lib/api";
import type { ChatMessage } from "@/types/api";

/**
 * Chat interface component for AI agent interactions.
 */
export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * Handle sending a message.
   */
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);

    // Add user message to chat
    const newUserMessage: ChatMessage = {
      role: "user",
      content: userMessage,
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: userMessage,
        conversation_id: conversationId,
      });

      // Update conversation ID
      setConversationId(response.conversation_id);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle keyboard events.
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * Clear the chat history.
   */
  const handleClear = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            AI Agent Chat
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Powered by LangGraph and RAG
          </p>
        </div>
        <button
          onClick={handleClear}
          className="px-3 py-1 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p className="text-lg mb-2">Welcome to the AI Agent</p>
              <p className="text-sm">
                Ask questions about your knowledge base or general topics.
              </p>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700"
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>

              {/* Show sources if available */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    Sources:
                  </p>
                  <div className="space-y-1">
                    {message.sources.map((source) => (
                      <div
                        key={source.id}
                        className="text-xs text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-2 rounded"
                      >
                        {source.content.substring(0, 100)}...
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg p-3 text-sm">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex space-x-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
