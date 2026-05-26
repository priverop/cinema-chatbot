const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type ChatTurn = { role: "user" | "assistant"; text: string };

export async function sendMessage(
  message: string,
  history: ChatTurn[],
): Promise<string> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail?.detail ?? `HTTP ${res.status}`);
  }
  const data: { reply: string } = await res.json();
  return data.reply;
}
