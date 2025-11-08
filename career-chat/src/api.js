import { API_BASE } from "./config";

export async function getHistory() {
  const r = await fetch(`${API_BASE}/chatmessages/`);
  return r.json();
}

export async function sendMessage(content) {
  const r = await fetch(`${API_BASE}/chatmessages/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  });
  return r.json();
}
