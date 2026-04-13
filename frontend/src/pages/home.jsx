import { useNavigate } from "react-router-dom";

const FEATURES = [
  {
    icon: "🧠",
    title: "Understands your code",
    desc: "Upload any codebase and ask questions in plain English. No setup, no config.",
  },
  {
    icon: "🎯",
    title: "Never gives you the answer",
    desc: "CodeSense explains and guides — it helps you think, not think for you.",
  },
  {
    icon: "🔗",
    title: "Traces impact",
    desc: "Ask what changes if you touch a function. See every caller and dependency.",
  },
  {
    icon: "💬",
    title: "Persistent chats",
    desc: "Your chats and code indexes are saved. Pick up exactly where you left off.",
  },
];

const LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "Go", "C", "C++", "Ruby", "Rust", "Swift", "Kotlin", "C#", "PHP", "Scala", "Dart", "Lua", "Elixir", "Perl", "Bash", "R"];

const EXAMPLES = [
  "How does the search route work?",
  "Where is authentication handled?",
  "What would break if I change this function?",
  "Explain what this code does in simple terms",
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div style={{ width: "min(960px, 92vw)", color: "white", margin: "0 auto", paddingBottom: 48 }}>

      {/* Hero */}
      <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
        <p style={{ opacity: 0.55, fontSize: "0.85rem", marginBottom: "0.6rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          CodeSense AI
        </p>
        <h1 style={{ fontSize: "clamp(2.4rem, 5vw, 3.8rem)", fontWeight: 800, lineHeight: 1.1, marginBottom: "1.2rem" }}>
          Understand any codebase{" "}
          <span style={{ color: "#38bdf8" }}>without being told the answer</span>
        </h1>
        <p style={{ fontSize: "1.05rem", opacity: 0.7, maxWidth: 620, margin: "0 auto 2rem", lineHeight: 1.7 }}>
          Upload your code files and ask anything. CodeSense explains how things work,
          shows what's connected, and guides you to the answer — like a mentor, not a search engine.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap" }}>
          <button
            onClick={() => navigate("/chat")}
            style={{
              padding: "0.85rem 2rem", fontSize: "1rem", borderRadius: 12,
              border: "none", background: "#38bdf8", color: "#020617",
              fontWeight: 700, cursor: "pointer",
            }}
          >
            Try it now →
          </button>
          <button
            onClick={() => window.open("http://localhost:8000/docs", "_blank")}
            style={{
              padding: "0.85rem 2rem", fontSize: "1rem", borderRadius: 12,
              background: "transparent", border: "1px solid rgba(255,255,255,0.2)",
              color: "white", cursor: "pointer",
            }}
          >
            API Docs
          </button>
        </div>
      </div>

      {/* Features */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: "3rem" }}>
        {FEATURES.map((f) => (
          <div key={f.title} style={{
            background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 14, padding: "1.2rem",
          }}>
            <div style={{ fontSize: "1.5rem", marginBottom: "0.6rem" }}>{f.icon}</div>
            <div style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.4rem" }}>{f.title}</div>
            <div style={{ fontSize: "0.82rem", opacity: 0.6, lineHeight: 1.6 }}>{f.desc}</div>
          </div>
        ))}
      </div>

      {/* Example questions + languages */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: "1.2rem" }}>
          <p style={{ opacity: 0.45, fontSize: "0.78rem", marginBottom: "0.9rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Example questions
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {EXAMPLES.map((q) => (
              <div key={q} onClick={() => navigate("/chat")} style={{
                padding: "0.5rem 0.9rem", borderRadius: 8, fontSize: "0.83rem",
                background: "rgba(56,189,248,0.06)", border: "1px solid rgba(56,189,248,0.15)",
                cursor: "pointer", opacity: 0.85,
              }}>
                "{q}"
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: "1.2rem" }}>
          <p style={{ opacity: 0.45, fontSize: "0.78rem", marginBottom: "0.9rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Supported languages
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {LANGUAGES.map((lang) => (
              <span key={lang} style={{
                padding: "0.35rem 0.8rem", borderRadius: 999, fontSize: "0.8rem",
                background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)",
                color: "#a5b4fc",
              }}>
                {lang}
              </span>
            ))}
          </div>
          <p style={{ opacity: 0.35, fontSize: "0.75rem", marginTop: "1rem" }}>
            Drop any file — CodeSense figures out the language automatically.
          </p>
        </div>

      </div>
    </div>
  );
}
