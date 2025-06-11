import React, { useState, useRef, useEffect } from "react";
import { sendChatMessage, analyzeResource } from "@/api/services/llama";
import { ChatMessage, ChatResponse } from "@/api/types";

interface Message {
  text: string;
  sender: "user" | "bot";
  loading?: boolean;
  error?: boolean;
  context?: {
    clusterInfo?: string;
    relatedResources?: string[];
    confidence?: number;
  };
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Hello! How can I help you with your Kubernetes cluster today?",
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    const userMessage: Message = { text: input, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");

    // Add loading message
    const loadingMessage: Message = {
      text: "Processing your request...",
      sender: "bot",
      loading: true,
    };
    setMessages((prevMessages) => [...prevMessages, loadingMessage]);

    try {
      // Call LLaMA API
      const response = await sendChatMessage({
        role: "user",
        content: input,
      });

      // Remove loading message
      setMessages((prevMessages) => prevMessages.filter((msg) => !msg.loading));

      // Add bot response
      const botResponse: Message = {
        text: response.message.content,
        sender: "bot",
        context: response.context,
      };
      setMessages((prevMessages) => [...prevMessages, botResponse]);
    } catch (error) {
      console.error("Error sending message to LLaMA API:", error);

      // Remove loading message
      setMessages((prevMessages) => prevMessages.filter((msg) => !msg.loading));

      // Add error message
      const errorMessage: Message = {
        text: "Sorry, I encountered an error processing your request. Please try again later.",
        sender: "bot",
        error: true,
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`rounded-lg p-3 max-w-xs ${
                message.sender === "user"
                  ? "bg-indigo-600 text-white"
                  : message.loading
                  ? "bg-gray-600 text-gray-100 animate-pulse"
                  : message.error
                  ? "bg-red-700 text-gray-100"
                  : "bg-gray-700 text-gray-100"
              }
              `}
            >
              {message.text}
              {message.context && message.context.confidence && (
                <div className="mt-2 text-xs text-gray-300">
                  Confidence: {Math.round(message.context.confidence * 100)}%
                </div>
              )}
              {message.context &&
                message.context.relatedResources &&
                message.context.relatedResources.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs text-gray-300 font-semibold">
                      Related Resources:
                    </div>
                    <ul className="text-xs text-gray-300 list-disc pl-4">
                      {message.context.relatedResources.map((resource, i) => (
                        <li key={i}>{resource}</li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex">
        <input
          type="text"
          className="flex-1 rounded-l-lg p-3 bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-indigo-500"
          placeholder="Ask me about your cluster..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter") {
              handleSendMessage();
            }
          }}
        />
        <button
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-r-lg transition duration-300 ease-in-out"
          onClick={handleSendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
