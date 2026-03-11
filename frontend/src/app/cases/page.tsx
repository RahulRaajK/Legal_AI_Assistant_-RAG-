"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import { useRouter } from "next/navigation";

export default function CasesPage() {
    const router = useRouter();
    const [cases, setCases] = useState<any[]>([]);
    const [showCreate, setShowCreate] = useState(false);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("");
    const [form, setForm] = useState({
        case_title: "", case_number: "", fir_number: "", case_code: "", act: "",
        case_type: "civil", petitioner: "", respondent: "", advocate_name: "",
        court_name: "", registration_number: "", description: "", facts: "",
        priority: "medium", next_hearing_date: "",
    });

    const loadCases = async () => {
        try {
            const data = await api.getCases(filter || undefined);
            setCases(data);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { loadCases(); }, [filter]);

    const createCase = async () => {
        try {
            await api.createCase(form);
            setShowCreate(false);
            setForm({ case_title: "", case_number: "", fir_number: "", case_code: "", act: "", case_type: "civil", petitioner: "", respondent: "", advocate_name: "", court_name: "", registration_number: "", description: "", facts: "", priority: "medium", next_hearing_date: "" });
            loadCases();
        } catch (e: any) { alert(e.message); }
    };

    const getBadgeClass = (status: string) => {
        switch (status) {
            case "active": return "badge-active";
            case "pending": return "badge-pending";
            case "urgent": return "badge-urgent";
            default: return "badge-closed";
        }
    };

    return (
        <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                <div>
                    <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 4px" }} className="gradient-text">Case Management</h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: "13px", margin: 0 }}>Track cases, hearings, documents & AI analysis</p>
                </div>
                <button className="btn-primary" onClick={() => setShowCreate(true)}>+ New Case</button>
            </div>

            {/* Filters */}
            <div style={{ display: "flex", gap: "8px", marginBottom: "20px", flexWrap: "wrap", borderBottom: "1px solid var(--border-color)", paddingBottom: "16px" }}>
                {["", "active", "pending", "closed"].map((f) => (
                    <button key={f} className={`role-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                        {f || "All"}
                    </button>
                ))}
            </div>

            {/* Case List Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "20px" }}>
                {loading ? (
                    <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "40px" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
                ) : cases.length === 0 ? (
                    <div className="glass-card" style={{ gridColumn: "1/-1", padding: "40px", textAlign: "center" }}>
                        <span style={{ fontSize: "48px", display: "block", marginBottom: "12px" }}>📂</span>
                        <p style={{ color: "var(--text-secondary)" }}>No cases yet. Create your first case to get started.</p>
                    </div>
                ) : (
                    cases.map((c) => (
                        <div key={c.id} className="search-result" style={{ cursor: "pointer", transition: "transform 0.2s" }}
                            onClick={() => router.push(`/cases/${c.id}`)}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "12px" }}>
                                <div>
                                    <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 6px", color: "var(--text-primary)" }}>{c.case_title}</h3>
                                    {c.petitioner && (
                                        <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "0 0 6px" }}>
                                            {c.petitioner} vs {c.respondent}
                                        </p>
                                    )}
                                    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                                        {c.case_number && <span style={{ fontSize: "11px", background: "var(--bg-secondary)", padding: "2px 6px", borderRadius: "12px", color: "var(--text-secondary)" }}>#{c.case_number}</span>}
                                        {c.fir_number && <span style={{ fontSize: "11px", background: "var(--bg-secondary)", padding: "2px 6px", borderRadius: "12px", color: "var(--text-secondary)" }}>FIR: {c.fir_number}</span>}
                                        <span style={{ fontSize: "11px", background: "var(--bg-secondary)", padding: "2px 6px", borderRadius: "12px", color: "var(--text-secondary)" }}>{c.case_type}</span>
                                    </div>
                                </div>
                                <span className={`badge ${getBadgeClass(c.status)}`}>{c.status}</span>
                            </div>
                            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                                    📍 {c.court_name || "Court not specified"}
                                </p>
                                <div style={{ display: "flex", gap: "12px" }}>
                                    {c.win_probability && (
                                        <span style={{ fontSize: "12px", color: "var(--accent-gold)", fontWeight: 600 }}>
                                            {Math.round(c.win_probability * 100)}% Win Prob
                                        </span>
                                    )}
                                    {c.next_hearing_date && (
                                        <span style={{ fontSize: "12px", color: "var(--accent-secondary)" }}>
                                            📅 {new Date(c.next_hearing_date).toLocaleDateString()}
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Create Case Modal */}
            {showCreate && (
                <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", backdropFilter: "blur(4px)", zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
                    <div className="glass-card" style={{ padding: "0", maxWidth: "800px", width: "100%", maxHeight: "90vh", overflowY: "auto", border: "1px solid var(--border-color)" }}>
                        <div style={{ padding: "24px", borderBottom: "1px solid var(--border-color)", display: "flex", justifyContent: "space-between", alignItems: "center", background: "var(--bg-secondary)" }}>
                            <h2 style={{ fontSize: "20px", fontWeight: 700, margin: 0 }} className="gradient-text">Register New Case (eCourts Format)</h2>
                            <button onClick={() => setShowCreate(false)} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "24px" }}>&times;</button>
                        </div>

                        <div style={{ padding: "24px", display: "grid", gap: "20px" }}>
                            {/* Section 1: Core Details */}
                            <div>
                                <h3 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-secondary)", marginBottom: "12px" }}>Case Details</h3>
                                <input className="input-field" placeholder="Case Title * (e.g., State vs John Doe)" value={form.case_title} onChange={(e) => setForm({ ...form, case_title: e.target.value })} style={{ marginBottom: "12px" }} />
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
                                    <input className="input-field" placeholder="Case Number" value={form.case_number} onChange={(e) => setForm({ ...form, case_number: e.target.value })} />
                                    <input className="input-field" placeholder="Case Code (CNR)" value={form.case_code} onChange={(e) => setForm({ ...form, case_code: e.target.value })} />
                                    <select className="input-field" value={form.case_type} onChange={(e) => setForm({ ...form, case_type: e.target.value })}>
                                        <option value="civil">Civil</option>
                                        <option value="criminal">Criminal</option>
                                        <option value="constitutional">Constitutional</option>
                                        <option value="family">Family</option>
                                        <option value="consumer">Consumer</option>
                                        <option value="labour">Labour</option>
                                        <option value="tax">Tax</option>
                                    </select>
                                </div>
                            </div>

                            {/* Section 2: Police & Act Details */}
                            <div>
                                <h3 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-secondary)", marginBottom: "12px" }}>First Information Report (FIR) / Act</h3>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                    <input className="input-field" placeholder="FIR Number (e.g., 102/2023)" value={form.fir_number} onChange={(e) => setForm({ ...form, fir_number: e.target.value })} />
                                    <input className="input-field" placeholder="Under Act(s) (e.g., IPC 302, 304)" value={form.act} onChange={(e) => setForm({ ...form, act: e.target.value })} />
                                </div>
                            </div>

                            {/* Section 3: Parties */}
                            <div>
                                <h3 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-secondary)", marginBottom: "12px" }}>Parties & Representation</h3>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px" }}>
                                    <input className="input-field" placeholder="Petitioner / Complainant" value={form.petitioner} onChange={(e) => setForm({ ...form, petitioner: e.target.value })} />
                                    <input className="input-field" placeholder="Respondent / Accused" value={form.respondent} onChange={(e) => setForm({ ...form, respondent: e.target.value })} />
                                </div>
                                <input className="input-field" placeholder="Advocate Name" value={form.advocate_name} onChange={(e) => setForm({ ...form, advocate_name: e.target.value })} />
                            </div>

                            {/* Section 4: Court Info */}
                            <div>
                                <h3 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-secondary)", marginBottom: "12px" }}>Court Allocation</h3>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px" }}>
                                    <input className="input-field" placeholder="Court Name" value={form.court_name} onChange={(e) => setForm({ ...form, court_name: e.target.value })} />
                                    <input className="input-field" placeholder="Registration Number" value={form.registration_number} onChange={(e) => setForm({ ...form, registration_number: e.target.value })} />
                                </div>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                    <input className="input-field" type="date" placeholder="Next Hearing Date" value={form.next_hearing_date} onChange={(e) => setForm({ ...form, next_hearing_date: e.target.value })} />
                                </div>
                            </div>

                            {/* Section 5: Summary */}
                            <div>
                                <h3 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-secondary)", marginBottom: "12px" }}>AI Briefing</h3>
                                <textarea className="input-field" placeholder="Case Description" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} style={{ resize: "vertical", marginBottom: "12px" }} />
                                <textarea className="input-field" placeholder="Case Facts (Crucial for AI Analysis - Describe what happened)" rows={4} value={form.facts} onChange={(e) => setForm({ ...form, facts: e.target.value })} style={{ resize: "vertical" }} />
                            </div>
                        </div>

                        <div style={{ padding: "24px", borderTop: "1px solid var(--border-color)", display: "flex", gap: "12px", justifyContent: "flex-end", background: "var(--bg-secondary)", borderBottomLeftRadius: "12px", borderBottomRightRadius: "12px" }}>
                            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                            <button className="btn-primary" onClick={createCase} disabled={!form.case_title}>📝 Register Case</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
