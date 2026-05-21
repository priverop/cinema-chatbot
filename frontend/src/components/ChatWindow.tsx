import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";

type Props = {
  messages: Message[];
  loading: boolean;
  onSend: (text: string) => void;
};

export function ChatWindow({ messages, loading, onSend }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {loading && (
          <div className="bubble-row assistant">
            <div className="bubble assistant typing">...</div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <MessageInput onSend={onSend} disabled={loading} />
    </div>
  );
}
