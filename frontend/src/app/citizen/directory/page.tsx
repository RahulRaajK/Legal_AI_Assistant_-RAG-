"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

export default function LawyerDirectory() {
    const [lawyers, setLawyers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const fetchLawyers = async () => {
            try {
                const data = await api.getLawyers();
                setLawyers(data);
            } catch (err) {
                console.error("Failed to fetch lawyers", err);
            } finally {
                setLoading(false);
            }
        };
        fetchLawyers();
    }, []);

    const filteredLawyers = lawyers.filter(l =>
        l.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        l.specialization?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
                <div>
                    <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }} className="gradient-text">
                        Lawyer Directory
                    </h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                        Browse registered advocates by name or legal specialization.
                    </p>
                </div>
                <div style={{ position: "relative", width: "300px" }}>
                    <span style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)" }}>
                        🔍
                    </span>
                    <input
                        type="text"
                        placeholder="Search lawyers or specialty..."
                        className="form-input"
                        style={{ paddingLeft: "40px" }}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)" }}>Loading directories...</div>
            ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "24px" }}>
                    {filteredLawyers.map((lawyer) => (
                        <div key={lawyer.id} className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", height: "100%" }}>
                            <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", marginBottom: "16px" }}>
                                <div style={{
                                    width: "60px", height: "60px", borderRadius: "12px",
                                    background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))",
                                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: "28px"
                                }}>
                                    👔
                                </div>
                                <div>
                                    <h3 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 4px" }}>{lawyer.full_name}</h3>
                                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                                        {lawyer.specialization?.split(',').map((spec: string, i: number) => (
                                            <span key={i} style={{
                                                fontSize: "11px", padding: "2px 8px", borderRadius: "4px",
                                                background: "rgba(99,102,241,0.1)", color: "#818cf8", border: "1px solid rgba(99,102,241,0.2)"
                                            }}>
                                                {spec.trim()}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, flex: 1, marginBottom: "16px" }}>
                                {lawyer.about || "No biographical information provided."}
                            </div>

                            <div style={{ marginTop: "auto", display: "flex", gap: "12px" }}>
                                <button className="btn-primary" style={{ flex: 1, padding: "8px", fontSize: "13px" }}>Request Consultation</button>
                            </div>
                        </div>
                    ))}

                    {filteredLawyers.length === 0 && (
                        <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "40px", color: "var(--text-secondary)", background: "var(--bg-card)", borderRadius: "12px", border: "1px dashed var(--border-color)" }}>
                            No lawyers found matching "{searchTerm}"
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
