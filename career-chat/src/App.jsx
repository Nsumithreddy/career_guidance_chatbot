import { useEffect, useRef, useState } from "react";
import "./App.css";
import { API_BASE } from "./config";
import React from 'react';

// Stable session per user/browser
const sessionId = (() => {
  let sid = localStorage.getItem("sid");
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem("sid", sid);
  }
  return sid;
})();

export default function App() {
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  // Load chat history
  useEffect(() => {
    fetch(`${API_BASE}/chatmessages/`, {
      headers: { "X-Session-Id": sessionId },
    })
      .then((r) => r.json())
      .then((data) => {
        const withTs = data.map((m) => ({ ts: Date.now(), ...m }));
        setMsgs(withTs);
      })
      .catch(console.error);
  }, []);

  // Auto-scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loading]);

  async function onSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    const userMsg = { id: Date.now(), role: "user", content: text, ts: Date.now() };
    setMsgs((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chatmessages/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Session-Id": sessionId,
        },
        body: JSON.stringify({ content: text }),
      });
      const bot = await res.json();
      setMsgs((m) => [...m, { ...bot, ts: Date.now() }]);
    } catch (err) {
      console.error(err);
      setMsgs((m) => [
        ...m,
        { id: Date.now(), role: "bot", content: "Server error. Try again.", ts: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Handle Enter and Shift+Enter
  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend(e);
    }
  }

  return (
    <div className="shell">
      <header className="topbar sticky">
        <div className="brand">Career Mentor</div>
        <div className="tag">Learning • Skills • Roadmaps</div>
      </header>

      <main className="chat">
        {msgs.map((m) => (
          <Message key={m.id} role={m.role} text={m.content} ts={m.ts} />
        ))}
        {loading && <TypingBubble />}
        <div ref={endRef} />
      </main>

      <form className="composer" onSubmit={onSend}>
        <input
          className="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask about skills, roadmaps, careers…"
        />
        <button className="send" disabled={loading || !input.trim()}>
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}

function Message({ role, text, ts }) {
  const isBot = role === "bot";
  const time = ts
    ? new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "";

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
    } catch {}
  }

  return (
    <div className={`row ${isBot ? "left" : "right"}`}>
      <div className={`avatar ${isBot ? "bot" : "user"}`}>{isBot ? "AI" : "You"}</div>
      <div className={`bubble ${isBot ? "bot" : "user"}`}>
        <div className="meta">
          <span className="time">{time}</span>
          {isBot && (
            <button className="copy" onClick={copy} title="Copy response" type="button">
              Copy
            </button>
          )}
        </div>
        {text}
      </div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="row left">
      <div className="avatar bot">AI</div>
      <div className="bubble bot typing">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  );
}
