import { Outlet, useNavigate } from "react-router-dom";

export default function AppLayout() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        background: "radial-gradient(circle at top, #1e293b, #020617)",
        color: "white",
      }}
    >
      {/* NAVBAR */}
      <header
        style={{
          height: 72,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          backdropFilter: "blur(12px)",
          background: "rgba(2,6,23,0.35)",
        }}
      >
        <div
          onClick={() => navigate("/")}
          style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}
        >
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 10,
              background: "linear-gradient(135deg, #38bdf8, #6366f1)",
            }}
          />
          <div style={{ fontWeight: 700 }}>CodeSense AI</div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            style={btnGhost}
          >
            GitHub
          </a>
          <button
            onClick={() => window.open("http://localhost:8000/docs", "_blank")}
            style={btnGhost}
          >
            API Docs
          </button>
          <button onClick={() => navigate("/chat")} style={btnPrimary}>
            Get Started →
          </button>
        </div>
      </header>

      {/* PAGE CONTENT */}
      <main
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "min(1200px, 100%)",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Outlet />
        </div>
      </main>
    </div>
  );
}

const btnGhost = {
  padding: "10px 14px",
  borderRadius: 999,
  border: "1px solid rgba(255,255,255,0.18)",
  background: "rgba(255,255,255,0.06)",
  color: "white",
  cursor: "pointer",
  textDecoration: "none",
  fontSize: 14,
};

const btnPrimary = {
  padding: "10px 14px",
  borderRadius: 999,
  border: "none",
  background: "#38bdf8",
  color: "#020617",
  cursor: "pointer",
  fontWeight: 700,
  fontSize: 14,
};