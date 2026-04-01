import { useState, useRef, useEffect, useCallback } from "react";
import { api } from "../lib/api";

const BASE_URL = "http://127.0.0.1:8000";

// ─── localStorage helpers ────────────────────────────────────────────────────

function loadState() {
  try {
    const raw = localStorage.getItem("codesense_chats");
    if (raw) return JSON.parse(raw);
  } catch {}
  return { chats: [], activeChatId: null };
}

function saveState(state) {
  localStorage.setItem("codesense_chats", JSON.stringify(state));
}

function newChat() {
  return {
    id: crypto.randomUUID(),
    name: "New Chat",
    messages: [],
    fileNames: [],
    createdAt: Date.now(),
  };
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function Chat() {
  const [state, setState] = useState(() => {
    const s = loadState();
    if (s.chats.length === 0) {
      const first = newChat();
      return { chats: [first], activeChatId: first.id };
    }
    return s;
  });

  const [question, setQuestion] = useState("");
  const [isIndexing, setIsIndexing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [indexRestored, setIndexRestored] = useState(false);
  const fileInputRef = useRef(null);
  const bottomRef = useRef(null);

  const activeChat = state.chats.find((c) => c.id === state.activeChatId);

  // Persist to localStorage whenever state changes
  useEffect(() => {
    saveState(state);
  }, [state]);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages]);

  // Restore the active chat's index from backend on mount / chat switch
  useEffect(() => {
    if (!activeChat) return;
    setIndexRestored(false);
    api(`/chats/${activeChat.id}/activate`, { method: "POST" })
      .then(() => setIndexRestored(true))
      .catch(() => setIndexRestored(false));
  }, [activeChat?.id]);

  const updateActiveChat = useCallback((patch) => {
    setState((prev) => ({
      ...prev,
      chats: prev.chats.map((c) =>
        c.id === prev.activeChatId ? { ...c, ...patch } : c
      ),
    }));
  }, []);

  const addMessage = useCallback((msg) => {
    updateActiveChat({
      messages: [...(activeChat?.messages ?? []), msg],
    });
  }, [activeChat, updateActiveChat]);

  // ── File upload ────────────────────────────────────────────────────────────

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;
    const fileList = Array.from(files);
    setIsIndexing(true);

    try {
      const formData = new FormData();
      fileList.forEach((f) => formData.append("files", f));
      formData.append("chat_id", activeChat.id);

      const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || `Upload failed: ${res.status}`);

      const fileNames = data.files;
      const chatName = fileNames.length === 1
        ? fileNames[0].replace(/\.[^.]+$/, "")
        : `${fileNames[0].replace(/\.[^.]+$/, "")} +${fileNames.length - 1}`;

      updateActiveChat({ fileNames, name: chatName });
      setIndexRestored(true);

      addMessage({
        role: "system",
        text: `Indexed ${data.chunks} chunks from ${fileNames.length} file${fileNames.length !== 1 ? "s" : ""}`,
      });
    } catch (e) {
      addMessage({ role: "system", text: `Error: ${e.message}` });
    } finally {
      setIsIndexing(false);
    }
  };

  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); handleFiles(e.dataTransfer.files); };
  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);

  // ── Ask ────────────────────────────────────────────────────────────────────

  const handleAsk = async () => {
    const q = question.trim();
    if (!q || isAsking) return;
    setQuestion("");
    addMessage({ role: "user", text: q });
    setIsAsking(true);

    try {
      const res = await api("/explain", {
        method: "POST",
        body: JSON.stringify({ question: q }),
      });
      addMessage({ role: "assistant", text: res.answer || "No answer returned.", results: res.results || [] });
    } catch (e) {
      addMessage({ role: "assistant", text: e.message, results: [] });
    } finally {
      setIsAsking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAsk(); }
  };

  // ── Chat management ────────────────────────────────────────────────────────

  const createNewChat = () => {
    const chat = newChat();
    setState((prev) => ({
      chats: [chat, ...prev.chats],
      activeChatId: chat.id,
    }));
    setIndexRestored(false);
  };

  const switchChat = (id) => {
    setState((prev) => ({ ...prev, activeChatId: id }));
  };

  const deleteChat = async (id, e) => {
    e.stopPropagation();
    try { await api(`/chats/${id}`, { method: "DELETE" }); } catch {}
    setState((prev) => {
      const chats = prev.chats.filter((c) => c.id !== id);
      if (chats.length === 0) {
        const fresh = newChat();
        return { chats: [fresh], activeChatId: fresh.id };
      }
      const activeChatId = prev.activeChatId === id ? chats[0].id : prev.activeChatId;
      return { chats, activeChatId };
    });
  };

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ display: "flex", height: "100%", width: "100%", gap: 16 }}>

      {/* Sidebar */}
      <div style={{
        width: 220,
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        gap: 6,
        borderRight: "1px solid #1e293b",
        paddingRight: 16,
      }}>
        <button onClick={createNewChat} style={newChatBtn}>+ New Chat</button>

        <div style={{ display: "flex", flexDirection: "column", gap: 4, overflowY: "auto" }}>
          {state.chats.map((c) => (
            <div
              key={c.id}
              onClick={() => switchChat(c.id)}
              style={{
                padding: "8px 10px",
                borderRadius: 8,
                cursor: "pointer",
                background: c.id === state.activeChatId ? "rgba(56,189,248,0.1)" : "transparent",
                border: c.id === state.activeChatId ? "1px solid rgba(56,189,248,0.25)" : "1px solid transparent",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 6,
              }}
            >
              <span style={{ fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", opacity: 0.85 }}>
                {c.name}
              </span>
              <button
                onClick={(e) => deleteChat(c.id, e)}
                style={{ background: "none", border: "none", color: "#475569", cursor: "pointer", fontSize: 14, lineHeight: 1, flexShrink: 0 }}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>

        {/* Drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !isIndexing && fileInputRef.current?.click()}
          style={{
            flexShrink: 0,
            marginBottom: 14,
            padding: "14px 20px",
            borderRadius: 12,
            border: `2px dashed ${isDragging ? "#38bdf8" : "#334155"}`,
            background: isDragging ? "rgba(56,189,248,0.06)" : "rgba(255,255,255,0.02)",
            cursor: isIndexing ? "not-allowed" : "pointer",
            textAlign: "center",
            transition: "all 0.15s ease",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".py,.js,.ts,.jsx,.tsx,.java"
            style={{ display: "none" }}
            onChange={(e) => handleFiles(e.target.files)}
          />
          {isIndexing ? (
            <span style={{ color: "#38bdf8", fontSize: 13 }}>Indexing…</span>
          ) : activeChat?.fileNames?.length > 0 ? (
            <div>
              <div style={{ fontSize: 13, color: "#38bdf8", marginBottom: 3 }}>
                ✓ {activeChat.fileNames.join(", ")}
              </div>
              <div style={{ fontSize: 11, opacity: 0.35 }}>Drop or click to replace</div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 13, opacity: 0.6, marginBottom: 3 }}>Drop code files here, or click to browse</div>
              <div style={{ fontSize: 11, opacity: 0.3 }}>Supports .py · .js · .ts · .jsx · .tsx · .java</div>
            </div>
          )}
        </div>

        {/* Index restore warning */}
        {activeChat?.fileNames?.length > 0 && !indexRestored && !isIndexing && (
          <div style={{ marginBottom: 10, padding: "8px 14px", borderRadius: 8, background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.2)", fontSize: 12, color: "#fbbf24" }}>
            Re-upload your files to restore the index for this chat.
          </div>
        )}

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 12, paddingRight: 4 }}>
          {(!activeChat?.messages || activeChat.messages.length === 0) && (
            <div style={{ textAlign: "center", opacity: 0.3, marginTop: 48, fontSize: 13 }}>
              Upload code files above, then ask anything about them.
            </div>
          )}

          {activeChat?.messages?.map((m, i) => {
            if (m.role === "user") return (
              <div key={i} style={{ alignSelf: "flex-end", maxWidth: "75%" }}>
                <div style={{ padding: "10px 14px", borderRadius: 14, background: "#38bdf8", color: "#020617", fontWeight: 500 }}>
                  {m.text}
                </div>
              </div>
            );

            if (m.role === "system") return (
              <div key={i} style={{ alignSelf: "center" }}>
                <div style={{ padding: "5px 14px", borderRadius: 999, background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)", fontSize: 12, color: "#a5b4fc" }}>
                  {m.text}
                </div>
              </div>
            );

            return (
              <div key={i} style={{ alignSelf: "flex-start", maxWidth: "85%" }}>
                <div style={{ background: "#1e293b", border: "1px solid #334155", padding: "14px 16px", borderRadius: 14 }}>
                  <p style={{ margin: "0 0 6px", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{m.text}</p>
                  {m.results?.length > 0 && <SourceSnippets results={m.results} />}
                </div>
              </div>
            );
          })}

          {isAsking && (
            <div style={{ alignSelf: "flex-start" }}>
              <div style={{ background: "#1e293b", border: "1px solid #334155", padding: "12px 16px", borderRadius: 14, fontSize: 13, opacity: 0.5 }}>
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{ display: "flex", gap: 8, marginTop: 12, flexShrink: 0 }}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything, or paste code in ```backticks```… (Enter to send)"
            rows={2}
            style={{
              flex: 1, background: "#0f172a", border: "1px solid #334155",
              borderRadius: 10, color: "white", padding: "10px 14px",
              fontSize: 14, outline: "none", resize: "none", lineHeight: 1.5,
            }}
          />
          <button
            onClick={handleAsk}
            disabled={isAsking || !question.trim()}
            style={{
              padding: "0 20px", borderRadius: 10, border: "none",
              background: "#38bdf8", color: "#020617", fontWeight: 700,
              fontSize: 14, flexShrink: 0,
              cursor: isAsking || !question.trim() ? "not-allowed" : "pointer",
              opacity: isAsking || !question.trim() ? 0.45 : 1,
            }}
          >
            {isAsking ? "…" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SourceSnippets({ results }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ marginTop: 8 }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{ background: "none", border: "none", color: "#64748b", fontSize: 12, cursor: "pointer", padding: 0 }}
      >
        {open ? "▾ Hide sources" : `▸ View ${results.length} source${results.length !== 1 ? "s" : ""}`}
      </button>
      {open && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
          {results.map((r, idx) => (
            <div key={idx} style={{ background: "#020617", border: "1px solid #1e293b", borderRadius: 10, padding: "10px 12px" }}>
              <div style={{ display: "flex", gap: 12, marginBottom: 6, fontSize: 12, opacity: 0.55 }}>
                <span>📄 {r.file}</span><span>⚙️ {r.function}</span>
              </div>
              <pre style={{ margin: 0, fontSize: 12, overflowX: "auto", lineHeight: 1.5 }}>{r.snippet}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const newChatBtn = {
  padding: "9px 14px", borderRadius: 8, border: "1px solid #334155",
  background: "rgba(255,255,255,0.04)", color: "white", fontSize: 13,
  cursor: "pointer", textAlign: "left", width: "100%",
};
