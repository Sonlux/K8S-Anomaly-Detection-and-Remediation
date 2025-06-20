import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, MessageCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import PodTable from "./PodTable";

interface Message {
  id: string;
  role: "user" | "assistant" | "pods";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatInterface = ({ isOpen, onClose }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [width, setWidth] = useState(384); // default 96 * 4 = 384px
  const [isResizing, setIsResizing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen && !conversationId) {
      createNewConversation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle drag events for resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const newWidth = Math.max(320, window.innerWidth - e.clientX - 16); // 16px right margin
      setWidth(Math.min(newWidth, 700)); // max width 700px
    };
    const handleMouseUp = () => setIsResizing(false);
    if (isResizing) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const createNewConversation = async () => {
    try {
      const { data, error } = await supabase
        .from("chat_conversations")
        .insert({ title: "Kubernetes Chat" })
        .select()
        .single();

      if (error) throw error;
      setConversationId(data.id);

      // Add welcome message
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content:
            "Hello! I'm your Kubernetes assistant. I can help you with cluster management, troubleshooting, and best practices. What would you like to know?",
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Error creating conversation:", error);
      toast({
        title: "Error",
        description: "Failed to create chat conversation",
        variant: "destructive",
      });
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      const responseText = data.response || "Sorry, I encountered an error.";

      const realTimeDataHeader = "--- Real-Time Kubernetes Data ---";
      const llmReasoningHeader = "--- LLM Reasoning & Guidance ---";

      let podDataContent = "";
      let llmSummaryContent = "";

      if (
        responseText.includes(realTimeDataHeader) &&
        responseText.includes(llmReasoningHeader)
      ) {
        const realTimeDataStartIndex =
          responseText.indexOf(realTimeDataHeader) + realTimeDataHeader.length;
        const llmReasoningStartIndex = responseText.indexOf(llmReasoningHeader);

        podDataContent = responseText
          .substring(realTimeDataStartIndex, llmReasoningStartIndex)
          .trim();
        llmSummaryContent = responseText
          .substring(
            responseText.indexOf(llmReasoningHeader) + llmReasoningHeader.length
          )
          .trim();
      } else {
        llmSummaryContent = responseText;
      }

      const newMessages: Message[] = [];
      const timestamp = new Date();

      // Add pods data first
      if (podDataContent) {
        newMessages.push({
          id: `${timestamp.getTime()}-pods`,
          role: "pods",
          content: podDataContent,
          timestamp: timestamp,
        });
      }

      // Then add the LLM summary
      if (llmSummaryContent) {
        newMessages.push({
          id: `${timestamp.getTime()}-assistant`,
          role: "assistant",
          content: llmSummaryContent,
          timestamp: timestamp,
        });
      }

      if (newMessages.length > 0) {
        setMessages((prev) => [...prev, ...newMessages]);
      } else {
        // Fallback for empty or unexpected response
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: "I did not receive a valid response.",
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error: unknown) {
      console.error("Error sending message:", error);
      let errorMessage = "Unknown error";
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast({
        title: "Error",
        description: `Failed to get AI response: ${errorMessage}. Please check if backend is running.`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      ref={chatRef}
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      style={{ width: width, minWidth: 320, maxWidth: 700 }}
      className="fixed right-4 top-20 bottom-4 bg-slate-800/95 backdrop-blur-lg border border-slate-700/50 rounded-lg shadow-2xl z-50 flex flex-col"
    >
      {/* Draggable Resizer */}
      <div
        style={{ left: -8 }}
        className="absolute top-0 bottom-0 w-3 cursor-ew-resize z-50"
        onMouseDown={() => setIsResizing(true)}
        title="Drag to resize"
      >
        <div className="h-full w-1 bg-slate-600 opacity-40 hover:opacity-80 rounded transition-opacity" />
      </div>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <span className="text-white font-medium">KODA</span>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white transition-colors"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex items-start space-x-2 max-w-[80%] ${
                  message.role === "user"
                    ? "flex-row-reverse space-x-reverse"
                    : ""
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === "user" ? "bg-blue-600" : "bg-slate-600"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="w-4 h-4 text-white" />
                  ) : message.role === "pods" ? (
                    <Bot className="w-4 h-4 text-green-300" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                <div
                  className={`p-3 rounded-lg ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : message.role === "pods"
                      ? "bg-slate-800 text-slate-100 border border-slate-700 w-full"
                      : "bg-slate-700 text-slate-100"
                  }`}
                >
                  {message.role === "pods" ? (
                    <pre className="whitespace-pre-wrap text-xs font-mono">
                      {message.content}
                    </pre>
                  ) : (
                    <div className="prose prose-sm prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-700/50">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your Kubernetes cluster..."
            className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-lg px-3 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface;
