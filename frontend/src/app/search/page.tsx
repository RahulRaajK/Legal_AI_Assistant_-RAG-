"use client";
import { useState } from "react";
import api from "@/lib/api";

export default function SearchPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchMode, setSearchMode] = useState("semantic");
    const [selectedResult, setSelectedResult] = useState<any>(null);

    const search = async () => {
        if (!query.trim()) return;
        setLoading(true);
        setSelectedResult(null);
        try {
            let data;
            switch (searchMode) {
                case "statutes":
                    data = await api.searchStatutes(query);
                    break;
                case "cases":
                    data = await api.searchCases(query);
                    break;
                case "graph":
                    data = await api.searchGraph(query);
                    break;
                default:
                    data = await api.semanticSearch(query);
            }
            setResults(data.results || []);
        } catch (e: any) {
            console.error(e);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const modes = [
        { value: "semantic", label: "🔍 Semantic", desc: "AI-powered meaning search" },
        { value: "statutes", label: "📜 Statutes", desc: "Search acts & sections" },
        { value: "cases", label: "⚖️ Cases", desc: "Search court judgments" },
        { value: "graph", label: "🕸️ Graph", desc: "Knowledge graph search" },
    ];

    return (
        <div>
            <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 4px" }} className="gradient-text">Legal Search</h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "20px" }}>
                Search across Indian statutes, court judgments, and legal knowledge graph
            </p>

            {/* Search Mode Tabs */}
            <div style={{ display: "flex", gap: "8px", marginBottom: "16px", flexWrap: "wrap" }}>
                {modes.map((m) => (
                    <button key={m.value} className={`role-btn ${searchMode === m.value ? "active" : ""}`} onClick={() => setSearchMode(m.value)} title={m.desc}>
                        {m.label}
                    </button>
                ))}
            </div>

            {/* Search Input */}
            <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
                <input
                    className="input-field"
                    placeholder={
                        searchMode === "statutes" ? "e.g., Article 21, Motor Vehicles Act..." :
                            searchMode === "cases" ? "e.g., right to privacy, murder conviction..." :
                                searchMode === "graph" ? "e.g., Constitution, IPC, Supreme Court..." :
                                    "Search anything about Indian law..."
                    }
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && search()}
                />
                <button className="btn-primary" onClick={search} disabled={loading || !query.trim()}>
                    {loading ? <div className="spinner" style={{ width: "16px", height: "16px" }} /> : "Search"}
                </button>
            </div>

            {/* Results */}
            <div style={{ display: "grid", gridTemplateColumns: selectedResult ? "1fr 1fr" : "1fr", gap: "20px" }}>
                <div>
                    {results.length > 0 && (
                        <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "12px" }}>
                            Found {results.length} results
                        </p>
                    )}
                    {results.map((r, i) => (
                        <div key={i} className="search-result" onClick={() => setSelectedResult(r)}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                                <div style={{ flex: 1 }}>
                                    <h3 style={{ fontSize: "14px", fontWeight: 700, margin: "0 0 4px", color: "var(--accent-secondary)" }}>
                                        {r.act_name || r.name || r.title || `Result ${i + 1}`}
                                    </h3>
                                    {r.section_number && (
                                        <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "4px", background: "rgba(245, 158, 11, 0.15)", color: "var(--accent-gold)" }}>
                                            Section {r.section_number}
                                        </span>
                                    )}
                                    {r.content_type && (
                                        <span style={{ fontSize: "11px", padding: "2px 8px", borderRadius: "4px", background: "rgba(99, 102, 241, 0.15)", color: "var(--accent-secondary)", marginLeft: "6px" }}>
                                            {r.content_type}
                                        </span>
                                    )}
                                </div>
                                {r.relevance_score !== undefined && (
                                    <span style={{ fontSize: "12px", color: "var(--accent-green)", fontWeight: 600 }}>
                                        {Math.round(r.relevance_score * 100)}%
                                    </span>
                                )}
                            </div>
                            {r.content && (
                                <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "8px 0 0", lineHeight: 1.6 }}>
                                    {r.content.substring(0, 200)}...
                                </p>
                            )}
                        </div>
                    ))}
                    {!loading && results.length === 0 && query && (
                        <div style={{ textAlign: "center", padding: "40px" }}>
                            <span style={{ fontSize: "48px", display: "block", marginBottom: "12px" }}>🔍</span>
                            <p style={{ color: "var(--text-secondary)" }}>No results found. Try different keywords.</p>
                        </div>
                    )}
                </div>

                {/* Detail Panel */}
                {selectedResult && (
                    <div className="glass-card" style={{ padding: "24px", maxHeight: "70vh", overflowY: "auto" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px" }}>
                            <h2 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>{selectedResult.act_name || selectedResult.name || "Details"}</h2>
                            <button className="btn-secondary" style={{ padding: "4px 10px", fontSize: "12px" }} onClick={() => setSelectedResult(null)}>✕</button>
                        </div>
                        {selectedResult.section_number && <p style={{ fontSize: "13px", color: "var(--accent-gold)", marginBottom: "8px" }}>Section {selectedResult.section_number}</p>}
                        {selectedResult.content_type && <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "12px" }}>Type: {selectedResult.content_type}</p>}
                        <p style={{ fontSize: "13px", lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                            {selectedResult.content || JSON.stringify(selectedResult, null, 2)}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
