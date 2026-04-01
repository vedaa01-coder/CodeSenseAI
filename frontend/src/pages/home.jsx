import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        width: "min(960px, 92vw)",
        textAlign: "center",
        transform: "translateY(-40px)", // lifts hero upward (important)
      }}
    >
      {/* Tagline */}
      <p
        style={{
          opacity: 0.65,
          marginBottom: "0.6rem",
          fontSize: "0.9rem",
        }}
      >
        CodeSense AI · Chat with your codebase
      </p>

      {/* Heading */}
      <h1
        style={{
          fontSize: "clamp(2.6rem, 5vw, 4rem)",
          fontWeight: 800,
          lineHeight: 1.1,
          marginBottom: "1rem",
        }}
      >
        Understand code{" "}
        <span style={{ color: "#38bdf8" }}>10× faster</span>
      </h1>

      {/* Description */}
      <p
        style={{
          fontSize: "1.1rem",
          opacity: 0.85,
          maxWidth: "700px",
          margin: "0 auto 2.2rem",
          lineHeight: 1.6,
        }}
      >
        Upload or point to a repository and ask questions like
        <br />
        <em>“Where is ingestion implemented?”</em> or{" "}
        <em>“How does indexing work?”</em>
        <br />
        Get answers grounded in real code.
      </p>

      {/* Buttons */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          marginBottom: "2.6rem",
          flexWrap: "wrap",
        }}
      >
        <button
          onClick={() => navigate("/chat")}
          style={{
            padding: "0.8rem 1.7rem",
            fontSize: "1rem",
            borderRadius: "12px",
            border: "none",
            background: "#38bdf8",
            color: "#020617",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Get Started →
        </button>

        <button
          onClick={() => window.open("http://localhost:8000/docs", "_blank")}
          style={{
            padding: "0.8rem 1.7rem",
            fontSize: "1rem",
            borderRadius: "12px",
            background: "transparent",
            border: "1px solid rgba(255,255,255,0.25)",
            color: "white",
            cursor: "pointer",
          }}
        >
          API Docs
        </button>
      </div>

      {/* Example box */}
      <div
        style={{
          background: "rgba(255,255,255,0.05)",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: "18px",
          padding: "1.4rem",
        }}
      >
        <p
          style={{
            opacity: 0.65,
            marginBottom: "0.8rem",
            fontSize: "0.85rem",
          }}
        >
          Example questions
        </p>

        <div
          style={{
            display: "flex",
            gap: "0.55rem",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {[
            "Where is ingestion logic implemented?",
            "How does indexing work?",
            "What files handle embeddings?",
            "Where are API routes defined?",
          ].map((q) => (
            <span
              key={q}
              style={{
                padding: "0.45rem 0.85rem",
                borderRadius: "999px",
                fontSize: "0.82rem",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.14)",
              }}
            >
              {q}
            </span>
          ))}
        </div>
      </div>

      {/* Footer hint */}
      <p
        style={{
          opacity: 0.4,
          marginTop: "2.2rem",
          fontSize: "0.75rem",
        }}
      >
        Local dev · Frontend 5173 · Backend 8000
      </p>
    </div>
  );
}