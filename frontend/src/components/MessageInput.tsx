import { useState, type FormEvent, type KeyboardEvent } from "react";

type Props = {
  onSend: (text: string) => void;
  disabled: boolean;
  lastUserMessage?: string;
};

export function MessageInput({ onSend, disabled, lastUserMessage }: Props) {
  const [text, setText] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowUp" && text === "" && lastUserMessage) {
      e.preventDefault();
      setText(lastUserMessage);
    }
  }

  return (
    <form className="message-input" onSubmit={submit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        disabled={disabled}
        autoFocus
      />
      <button type="submit" disabled={disabled || !text.trim()}>
        Send
      </button>
    </form>
  );
}
