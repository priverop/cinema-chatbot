import type { Message } from "../types";

export function MessageBubble({ message }: { message: Message }) {
  return (
    <div className={`bubble-row ${message.role}`}>
      <div className={`bubble ${message.role}`}>{message.text}</div>
    </div>
  );
}
