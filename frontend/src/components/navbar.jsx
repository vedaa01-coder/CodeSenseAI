import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        backdropFilter: "blur(10px)",
        background: "rgba(2, 6, 23, 0.55)",
        borderBottom: "1px solid rgba(255,255,255,0.10)",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
          padding: "0.9rem 1.25rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
        }}
      >
        {/* Left */}
        <Link
          to="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            color: "white",
            textDecoration: "none",
            fontWeight: 800,
            letterSpacing: "0.2px",
          }}
        >
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 10,
              background:
                "linear-gradient(135deg, rgba(56,189,248,0.95), rgba(99,102,241,0.95))",
              boxShadow: "0 10px 25px rgba(56,189,248,0.15)",
            }}
          />
          <span style={{ fontSize: "1.05rem" }}>CodeSense AI</span>
        </Link>

        {/* Right */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button
            onClick={() => window.open("https://github.com/vedaa01-coder/CodeSense-AI", "_blank")}
            style={btnGhost}
          >
            GitHub
          </button>

          <button
            onClick={() => window.open("http://localhost:8000/docs", "_blank")}
            style={btnGhost}
          >
            API Docs
          </button>

          <button
            onClick={() => navigate("/chat")}
            style={btnPrimary}
          >
            Get Started →
          </button>
        </div>
      </div>
    </div>
  );
}

const btnGhost = {
  padding: "0.55rem 0.9rem",
  borderRadius: 12,
  background: "rgba(255,255,255,0.06)",
  border: "1px solid rgba(255,255,255,0.14)",
  color: "white",
  cursor: "pointer",
  fontWeight: 600,
};

const btnPrimary = {
  padding: "0.55rem 0.95rem",
  borderRadius: 12,
  background: "#38bdf8",
  border: "none",
  color: "#020617",
  cursor: "pointer",
  fontWeight: 800,
};