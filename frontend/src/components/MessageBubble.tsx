import type { Message } from "../types";

function renderBold(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i}>{part.slice(2, -2)}</strong>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

export function MessageBubble({ message }: { message: Message }) {
  return (
    <div className={`bubble-row ${message.role}`}>
      <div className={`bubble ${message.role}`}>{renderBold(message.text)}</div>
    </div>
  );
}
