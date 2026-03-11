"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import api from "@/lib/api";

export default function Dashboard() {
    const [stats, setStats] = useState<any>(null);
    const [health, setHealth] = useState<any>(null);
    const [upcomingHearings, setUpcomingHearings] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [userRole, setUserRole] = useState("");
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        setUserRole(localStorage.getItem("user_role") || "citizen");
        const loadData = async () => {
            try {
                const [healthData, statsData, casesData] = await Promise.all([
                    api.healthCheck().catch(() => null),
                    api.getSearchStats().catch(() => null),
                    api.getCases().catch(() => []),
                ]);
                setHealth(healthData);
                setStats(statsData);

                // Filter to only cases that have a future hearing date and take top 3
                const now = new Date();
                const upcoming = casesData
                    .filter((c: any) => c.next_hearing_date && new Date(c.next_hearing_date) >= now)
                    .slice(0, 3);
                setUpcomingHearings(upcoming);

            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    const features = [
        { title: "AI Legal Chat", desc: "Ask any question about Indian law", icon: "🤖", href: "/chat", color: "#6366f1" },
        { title: "Case Management", desc: "Track cases, hearings & documents", icon: "📂", href: "/cases", color: "#10b981" },
        { title: "Legal Search", desc: "Search statutes, cases & precedents", icon: "🔍", href: "/search", color: "#f59e0b" },
        { title: "Document Analysis", desc: "Upload & analyze legal documents", icon: "📄", href: "/documents", color: "#ec4899" },
        { title: "Win Probability", desc: "AI-powered case success prediction", icon: "📊", href: "/cases", color: "#8b5cf6" },
        { title: "Law Updates", desc: "Monitor new laws & amendments", icon: "🌐", href: "/crawler", color: "#06b6d4" },
    ];

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: "32px" }}>
                <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }}>
                    <span className="gradient-text">Legal AI Assistant</span>
                </h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                    AI-powered assistant for Indian Law — Statutes, Case Histories & Legal Reasoning
                </p>
            </div>

            {/* Stats Row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "32px" }}>
                <div className="stat-card">
                    <div className="stat-value">{stats?.vector_store?.total_documents || 0}</div>
                    <div className="stat-label">Legal Documents Indexed</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats?.knowledge_graph?.total_nodes || 0}</div>
                    <div className="stat-label">Knowledge Graph Nodes</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats?.knowledge_graph?.total_edges || 0}</div>
                    <div className="stat-label">Legal Relationships</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{
                        background: health?.ollama_connected ? "linear-gradient(135deg, #10b981, #059669)" : "linear-gradient(135deg, #ef4444, #dc2626)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent"
                    }}>
                        {health?.ollama_connected ? "Online" : "Offline"}
                    </div>
                    <div className="stat-label">AI Engine ({health?.ollama_model || "N/A"})</div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 350px", gap: "24px", marginBottom: "32px", alignItems: "start" }}>
                {/* Quick Access Grid */}
                <div>
                    <h2 style={{ fontSize: "18px", fontWeight: 700, marginBottom: "16px" }}>Quick Access</h2>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
                        {mounted && features
                            .filter(f => !(f.title === "Win Probability" && userRole === "judge"))
                            .map((f) => (
                                <Link key={f.title} href={f.href} style={{ textDecoration: "none", color: "inherit" }}>
                                    <div className="glass-card" style={{ padding: "20px", cursor: "pointer", height: "100%" }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
                                            <span style={{ fontSize: "24px" }}>{f.icon}</span>
                                            <h3 style={{ fontSize: "15px", fontWeight: 700, margin: 0 }}>{f.title}</h3>
                                        </div>
                                        <p style={{ color: "var(--text-secondary)", fontSize: "12px", margin: 0, lineHeight: 1.5 }}>
                                            {f.desc}
                                        </p>
                                        <div style={{ marginTop: "16px", height: "3px", borderRadius: "2px", background: `linear-gradient(90deg, ${f.color}, transparent)` }} />
                                    </div>
                                </Link>
                            ))}
                    </div>
                </div>

                {/* Upcoming Hearings */}
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                        <h2 style={{ fontSize: "18px", fontWeight: 700, margin: 0 }}>Upcoming Hearings</h2>
                        <Link href="/cases" style={{ fontSize: "13px", color: "var(--text-secondary)", textDecoration: "none" }}>View All</Link>
                    </div>

                    <div className="glass-card" style={{ padding: "0", overflow: "hidden" }}>
                        {loading ? (
                            <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>Loading...</div>
                        ) : upcomingHearings.length === 0 ? (
                            <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
                                No upcoming hearings scheduled.
                            </div>
                        ) : (
                            <div style={{ display: "flex", flexDirection: "column" }}>
                                {upcomingHearings.map((h, i) => (
                                    <Link key={h.id} href={`/cases/${h.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                                        <div style={{
                                            padding: "16px",
                                            borderBottom: i < upcomingHearings.length - 1 ? "1px solid var(--border-color)" : "none",
                                            transition: "background 0.2s",
                                        }} className="hover:bg-[rgba(255,255,255,0.02)]">
                                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                                                <span style={{ fontWeight: 600, fontSize: "14px", color: "#6366f1" }}>{new Date(h.next_hearing_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span>
                                                <span style={{ fontSize: "12px", color: "var(--text-secondary)", background: "rgba(255,255,255,0.05)", padding: "2px 6px", borderRadius: "4px" }}>
                                                    {h.hearing_time || "TBD"}
                                                </span>
                                            </div>
                                            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "4px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                                                {h.case_title}
                                            </div>
                                            <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                                                {h.case_type || "General"} • {h.court_name || "Unassigned"}
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Quick Chat */}
            <div className="glass-card" style={{ padding: "24px" }}>
                <h2 style={{ fontSize: "18px", fontWeight: 700, marginBottom: "12px" }}>⚡ Quick Legal Query</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "16px" }}>
                    Try: &quot;What does Article 21 mean?&quot; • &quot;Cases related to right to privacy&quot; • &quot;Explain Section 302 IPC&quot;
                </p>
                <Link href="/chat">
                    <button className="btn-primary">🤖 Start AI Chat</button>
                </Link>
            </div>
        </div>
    );
}
