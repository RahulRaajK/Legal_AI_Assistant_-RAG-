"use client";
import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson(path: string) {
    const token = localStorage.getItem("auth_token");
    const res = await fetch(`${API_BASE}${path}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    return res.ok ? res.json() : null;
}

export default function CrawlerPage() {
    const [source, setSource] = useState("indiankanoon");
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [ingesting, setIngesting] = useState<string | null>(null);
    const [ingestStatus, setIngestStatus] = useState<Record<string, string>>({});

    const [corpusStats, setCorpusStats] = useState<any>(null);
    const [monitorStatus, setMonitorStatus] = useState<any>(null);
    const [recentUpdates, setRecentUpdates] = useState<any[]>([]);
    const [monitorRunning, setMonitorRunning] = useState(false);

    const loadLiveData = useCallback(async () => {
        const [stats, monitor, updates] = await Promise.all([
            fetchJson("/api/crawler/corpus-stats"),
            fetchJson("/api/crawler/monitor-status"),
            fetchJson("/api/crawler/law-updates?limit=15"),
        ]);
        if (stats) setCorpusStats(stats);
        if (monitor) setMonitorStatus(monitor);
        if (updates) setRecentUpdates(updates.updates || []);
    }, []);

    useEffect(() => {
        loadLiveData();
        const interval = setInterval(loadLiveData, 30000); // Auto-refresh every 30s
        return () => clearInterval(interval);
    }, [loadLiveData]);

    const triggerMonitor = async () => {
        setMonitorRunning(true);
        try {
            const token = localStorage.getItem("auth_token");
            await fetch(`${API_BASE}/api/crawler/monitor-run-now`, {
                method: "POST",
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            setTimeout(() => {
                loadLiveData();
                alert("Live monitor check triggered successfully in the background!");
            }, 3000);
        } finally {
            setTimeout(() => setMonitorRunning(false), 3000);
        }
    };

    const search = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const data = await api.crawlSearch(source, query);
            setResults(data.results || []);
        } catch (e: any) { alert(e.message); }
        finally { setLoading(false); }
    };

    const ingest = async (url: string) => {
        setIngesting(url);
        try {
            await api.fetchAndIngest(url, source);
            setIngestStatus((prev) => ({ ...prev, [url]: "queued" }));
        } catch (e: any) { alert(e.message); }
        finally { setIngesting(null); }
    };

    const embedded = corpusStats?.total_embedded ?? 0;
    const pending = corpusStats?.total_pending ?? 0;
    const failed = corpusStats?.total_failed ?? 0;
    const total = corpusStats?.vector_store?.total_documents ?? 0;
    const progress = total > 0 ? Math.min(100, Math.round((embedded / Math.max(total, 6450)) * 100)) : 0;

    return (
        <div>
            <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 4px" }} className="gradient-text">
                Live Law Monitor & Corpus
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "24px" }}>
                Real-time monitoring of Indian legal corpus — Constitution, Central Acts, State Laws & Amendments
            </p>

            {/* Corpus Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "16px", marginBottom: "24px" }}>
                {[
                    { label: "Total Indexed", value: total.toLocaleString(), color: "var(--accent-primary)", icon: "📚" },
                    { label: "Embedded ✅", value: embedded.toLocaleString(), color: "#10b981", icon: "✅" },
                    { label: "Pending ⏳", value: pending.toLocaleString(), color: "#f59e0b", icon: "⏳" },
                    { label: "Failed ❌", value: failed.toLocaleString(), color: "#ef4444", icon: "❌" },
                ].map((s) => (
                    <div key={s.label} className="stat-card" style={{ padding: "16px" }}>
                        <div style={{ fontSize: "20px", marginBottom: "4px" }}>{s.icon}</div>
                        <div className="stat-value" style={{ fontSize: "22px", color: s.color }}>{s.value}</div>
                        <div className="stat-label">{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Live Monitor Card */}
            <div className="glass-card" style={{ padding: "24px", marginBottom: "24px", borderLeft: "3px solid var(--accent-primary)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
                    <div>
                        <h2 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 6px" }}>🔴 Live Amendment Monitor</h2>
                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: "0 0 8px" }}>
                            Polls IndiaCode every hour for new laws, acts, and constitutional amendments
                        </p>
                        <div style={{ display: "flex", gap: "16px", fontSize: "12px", color: "var(--text-secondary)" }}>
                            <span>📅 Last run: <b style={{ color: "var(--text-primary)" }}>{monitorStatus?.last_run ? new Date(monitorStatus.last_run).toLocaleTimeString() : "—"}</b></span>
                            <span>🔁 Checks done: <b style={{ color: "var(--text-primary)" }}>{monitorStatus?.total_checks ?? 0}</b></span>
                            <span>🆕 New laws found: <b style={{ color: "#10b981" }}>{monitorStatus?.total_new_laws_detected ?? 0}</b></span>
                        </div>
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                        <button className="btn-secondary" style={{ fontSize: "12px", padding: "8px 16px" }} onClick={() => { loadLiveData(); alert("Live stats refreshed!"); }}>
                            🔄 Refresh
                        </button>
                        <button className="btn-primary" style={{ fontSize: "12px", padding: "8px 16px" }} onClick={triggerMonitor} disabled={monitorRunning}>
                            {monitorRunning ? "⏳ Running..." : "▶ Run Now"}
                        </button>
                    </div>
                </div>

                {/* Ingestion Progress Bar */}
                <div style={{ marginTop: "20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "12px" }}>
                        <span style={{ color: "var(--text-secondary)" }}>Corpus Ingestion Progress</span>
                        <span style={{ color: "var(--accent-primary)", fontWeight: 700 }}>{progress}% of ~6,450 laws</span>
                    </div>
                    <div style={{ height: "8px", background: "rgba(255,255,255,0.08)", borderRadius: "4px", overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #6366f1, #8b5cf6)", borderRadius: "4px", transition: "width 0.5s ease" }} />
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: "6px", fontSize: "11px", color: "var(--text-secondary)" }}>
                        <span>448 Articles • 25 Parts • 12 Schedules • 106 Amendments</span>
                        <span>859 Central Acts • 5,000+ State Laws</span>
                    </div>
                </div>
            </div>

            {/* Recently Indexed Laws */}
            {recentUpdates.length > 0 && (
                <div className="glass-card" style={{ padding: "24px", marginBottom: "24px" }}>
                    <h2 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>🆕 Recently Indexed / Updated Laws</h2>
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                        {recentUpdates.map((u, i) => (
                            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px", borderRadius: "8px", background: "rgba(255,255,255,0.04)", fontSize: "13px" }}>
                                <div>
                                    <span style={{ fontWeight: 600 }}>{u.title}</span>
                                    <span style={{ marginLeft: "8px", fontSize: "11px", color: "var(--text-secondary)" }}>{u.content_type} • {u.source}</span>
                                </div>
                                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                    {u.last_updated && (
                                        <span style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
                                            {new Date(u.last_updated).toLocaleDateString("en-IN")}
                                        </span>
                                    )}
                                    <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "12px", background: "rgba(16,185,129,0.15)", color: "#10b981" }}>
                                        ✅ Indexed
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Search & Import */}
            <div className="glass-card" style={{ padding: "24px" }}>
                <h2 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>🌐 Manual Search & Import</h2>
                <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
                    <button className={`role-btn ${source === "indiankanoon" ? "active" : ""}`} onClick={() => setSource("indiankanoon")}>⚖️ Indian Kanoon</button>
                    <button className={`role-btn ${source === "indiacode" ? "active" : ""}`} onClick={() => setSource("indiacode")}>📜 IndiaCode</button>
                </div>
                <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
                    <input
                        className="input-field"
                        placeholder={source === "indiankanoon" ? "Search cases... e.g., Kesavananda Bharati" : "Search acts... e.g., Motor Vehicles Act"}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && search()}
                    />
                    <button className="btn-primary" onClick={search} disabled={loading || !query.trim()}>
                        {loading ? <div className="spinner" style={{ width: "16px", height: "16px" }} /> : "Search"}
                    </button>
                </div>
                {results.map((r, i) => (
                    <div key={i} className="search-result">
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <div style={{ flex: 1, marginRight: "12px" }}>
                                <h3 style={{ fontSize: "14px", fontWeight: 600, margin: "0 0 4px" }}>{r.title}</h3>
                                <p style={{ fontSize: "11px", color: "var(--text-secondary)", margin: 0 }}>{r.source} {r.year && `• ${r.year}`}</p>
                            </div>
                            <div style={{ display: "flex", gap: "8px" }}>
                                <a href={r.url} target="_blank" rel="noopener noreferrer" className="btn-secondary" style={{ padding: "6px 12px", fontSize: "12px", textDecoration: "none" }}>🔗 View</a>
                                <button className="btn-primary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => ingest(r.url)} disabled={ingesting === r.url || ingestStatus[r.url] === "queued"}>
                                    {ingestStatus[r.url] === "queued" ? "✅ Imported" : ingesting === r.url ? "..." : "📥 Import"}
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
