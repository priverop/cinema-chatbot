import { useState } from "react";
import { ChatWindow } from "./components/ChatWindow";
import { sendMessage } from "./api/chat";
import type { Message } from "./types";

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSend(text: string) {
    const userMsg: Message = { id: uid(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    try {
      const reply = await sendMessage(text);
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "assistant", text: reply },
      ]);
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "error", text: `Error: ${detail}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="app-header">
        <h2>Cinema Assistant</h2>
      </header>
      <ChatWindow messages={messages} loading={loading} onSend={handleSend} />
    </main>
  );
}
