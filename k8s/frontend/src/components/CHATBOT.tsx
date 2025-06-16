import { useState } from "react";

export default function ChatbotUI() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "bot"; text: string }[]
  >([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();

      const botMsg = {
        role: "bot",
        text: data.answer || "No response received.",
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error connecting to chatbot." },
      ]);
      console.error("Chatbot error:", error);
    }
  };

  return (
    <div className="w-full h-full flex flex-col overflow-hidden border dark:border-gray-700">
      <div className="bg-blue-600 dark:bg-blue-800 text-white px-4 py-2 font-bold">
        K8s Chatbot
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2 text-sm">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-2 rounded-md ${
              m.role === "user"
                ? "bg-blue-100 dark:bg-blue-950 text-right"
                : "bg-gray-100 dark:bg-gray-800"
            }`}
          >
            {m.text}
          </div>
        ))}
      </div>
      <div className="p-2 border-t dark:border-gray-700 flex items-center gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-2 py-1 border rounded-md text-sm dark:bg-gray-800 dark:text-white"
          placeholder="Ask something..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}
