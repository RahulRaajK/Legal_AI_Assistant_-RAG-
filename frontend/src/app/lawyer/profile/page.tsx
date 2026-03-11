"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

export default function LawyerProfile() {
    const [profile, setProfile] = useState<any>(null);
    const [editing, setEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        full_name: "",
        bar_council_id: "",
        specialization: "",
        about: "",
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await api.getMe();
                setProfile(data);
                setFormData({
                    full_name: data.full_name || "",
                    bar_council_id: data.bar_council_id || "",
                    specialization: data.specialization || "",
                    about: data.about || "",
                });
            } catch (err) {
                console.error("Failed to load profile", err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const updated = await api.updateProfile(formData);
            setProfile(updated);
            setEditing(false);
        } catch (err) {
            console.error("Failed to save profile", err);
            alert("Failed to save profile updates.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div style={{ padding: "40px", color: "var(--text-secondary)", textAlign: "center" }}>Loading Profile...</div>;

    return (
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
                <div>
                    <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }} className="gradient-text">
                        Advocate Profile
                    </h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                        Manage your public information displayed in the Citizen Lawyer Directory.
                    </p>
                </div>
                {!editing ? (
                    <button className="btn-secondary" onClick={() => setEditing(true)}>Edit Profile</button>
                ) : (
                    <div style={{ display: "flex", gap: "12px" }}>
                        <button className="btn-secondary" onClick={() => setEditing(false)} disabled={saving}>Cancel</button>
                        <button className="btn-primary" onClick={handleSave} disabled={saving}>
                            {saving ? "Saving..." : "Save Changes"}
                        </button>
                    </div>
                )}
            </div>

            <div className="glass-card" style={{ padding: "32px", display: "flex", flexDirection: "column", gap: "24px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "24px", paddingBottom: "24px", borderBottom: "1px solid var(--border-color)" }}>
                    <div style={{
                        width: "80px", height: "80px", borderRadius: "20px",
                        background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))",
                        display: "flex", alignItems: "center", justifyContent: "center", fontSize: "36px"
                    }}>
                        👔
                    </div>
                    <div style={{ flex: 1 }}>
                        {editing ? (
                            <div className="input-group" style={{ marginBottom: "8px" }}>
                                <label>Full Name (with Title)</label>
                                <input type="text" name="full_name" className="form-input" value={formData.full_name} onChange={handleChange} />
                            </div>
                        ) : (
                            <h2 style={{ fontSize: "24px", fontWeight: 700, margin: "0 0 4px" }}>{profile.full_name}</h2>
                        )}
                        <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0 }}>
                            {profile.email} • Username: {profile.username}
                        </p>
                    </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
                    <div>
                        <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                            Bar Council ID
                        </h3>
                        {editing ? (
                            <input type="text" name="bar_council_id" className="form-input" value={formData.bar_council_id} onChange={handleChange} />
                        ) : (
                            <div style={{ fontSize: "16px", fontWeight: 500 }}>{profile.bar_council_id || "Not Provided"}</div>
                        )}
                    </div>

                    <div>
                        <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                            Specialization Areas
                        </h3>
                        {editing ? (
                            <input type="text" name="specialization" className="form-input" placeholder="e.g. Criminal, Corporate, IP" value={formData.specialization} onChange={handleChange} />
                        ) : (
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                                {profile.specialization ? profile.specialization.split(',').map((spec: string, i: number) => (
                                    <span key={i} style={{
                                        fontSize: "13px", padding: "4px 12px", borderRadius: "6px",
                                        background: "rgba(99,102,241,0.1)", color: "#818cf8", border: "1px solid rgba(99,102,241,0.2)"
                                    }}>
                                        {spec.trim()}
                                    </span>
                                )) : <span style={{ color: "var(--text-secondary)" }}>None specified</span>}
                            </div>
                        )}
                    </div>
                </div>

                <div>
                    <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                        About You (Public Bio)
                    </h3>
                    {editing ? (
                        <textarea
                            name="about"
                            className="form-input"
                            rows={5}
                            placeholder="Write a brief professional biography for potential clients..."
                            value={formData.about}
                            onChange={handleChange}
                        />
                    ) : (
                        <div style={{
                            fontSize: "15px", lineHeight: 1.6, color: profile.about ? "inherit" : "var(--text-secondary)",
                            background: "rgba(255,255,255,0.02)", padding: "16px", borderRadius: "12px", border: "1px solid var(--border-color)"
                        }}>
                            {profile.about || "Your biography is empty. Add details to attract clients in the directory."}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
