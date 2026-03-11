import Link from "next/link";

export default function LandingPage() {
  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "40px 20px",
      textAlign: "center",
      background: "var(--bg-default)",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Background Glow */}
      <div style={{
        position: "absolute",
        top: "-10%",
        left: "50%",
        transform: "translateX(-50%)",
        width: "600px",
        height: "600px",
        background: "radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)",
        zIndex: 0,
        pointerEvents: "none"
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: "800px" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "12px", marginBottom: "24px" }}>
          <span style={{ fontSize: "48px" }}>⚖️</span>
          <h1 style={{ fontSize: "42px", fontWeight: 900, margin: 0 }} className="gradient-text">
            Legal AI Assistant
          </h1>
        </div>

        <p style={{ fontSize: "18px", color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: "48px" }}>
          The intelligent platform for Indian Law. Access advanced case management, semantic legal search, and AI-powered evidence analysis tailored for Judges, Lawyers, and Citizens.
        </p>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "24px",
          width: "100%",
          maxWidth: "900px"
        }}>
          {/* Judge Card */}
          <Link href="/auth?role=judge" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
            <div className="glass-card" style={{ padding: "32px 24px", transition: "all 0.3s ease", cursor: "pointer", height: "100%" }}>
              <div style={{ fontSize: "40px", marginBottom: "16px" }}>👨‍⚖️</div>
              <h2 style={{ fontSize: "20px", fontWeight: 700, margin: "0 0 12px" }}>For Judges</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0, lineHeight: 1.5 }}>
                Access court calendars, manage evidence admissibility, and cross-reference statutes instantly.
              </p>
            </div>
          </Link>

          {/* Lawyer Card */}
          <Link href="/auth?role=lawyer" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
            <div className="glass-card" style={{ padding: "32px 24px", transition: "all 0.3s ease", cursor: "pointer", height: "100%" }}>
              <div style={{ fontSize: "40px", marginBottom: "16px" }}>👔</div>
              <h2 style={{ fontSize: "20px", fontWeight: 700, margin: "0 0 12px" }}>For Lawyers</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0, lineHeight: 1.5 }}>
                Build arguments with AI, manage client dockets, and find case precedents rapidly.
              </p>
            </div>
          </Link>

          {/* Citizen Card */}
          <Link href="/auth?role=citizen" style={{ textDecoration: "none", color: "inherit", display: "block" }}>
            <div className="glass-card" style={{ padding: "32px 24px", transition: "all 0.3s ease", cursor: "pointer", height: "100%" }}>
              <div style={{ fontSize: "40px", marginBottom: "16px" }}>👤</div>
              <h2 style={{ fontSize: "20px", fontWeight: 700, margin: "0 0 12px" }}>For Citizens</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0, lineHeight: 1.5 }}>
                Explain your incident to the AI to find filing sections, track your personal cases, and find lawyers.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
