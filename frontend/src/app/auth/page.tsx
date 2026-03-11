"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api from "@/lib/api";

function AuthContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialRole = searchParams.get("role") || "citizen";
    const [isLogin, setIsLogin] = useState(true);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    // Form Data
    const [formData, setFormData] = useState({
        username: "",
        password: "",
        email: "",
        full_name: "",
        role: initialRole,
        bar_council_id: "",
        court_name: "",
        specialization: "",
        about: ""
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (isLogin) {
                // Login Flow
                const response = await api.login(formData.username, formData.password);
                localStorage.setItem("auth_token", response.access_token);
                localStorage.setItem("user_role", response.user.role);
                router.push("/dashboard");
            } else {
                // Register Flow
                const response = await fetch("http://localhost:8000/api/auth/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email: formData.email,
                        username: formData.username,
                        full_name: formData.full_name,
                        password: formData.password,
                        role: formData.role,
                        bar_council_id: formData.role === "lawyer" ? formData.bar_council_id : null,
                        court_name: formData.role === "judge" ? formData.court_name : null,
                        specialization: formData.role === "lawyer" ? formData.specialization : null,
                        about: formData.role === "lawyer" ? formData.about : null,
                    }),
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Registration failed");

                localStorage.setItem("auth_token", data.access_token);
                localStorage.setItem("user_role", data.user.role);
                router.push("/dashboard");
            }
        } catch (err: any) {
            setError(err.message || "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
            background: "var(--bg-default)",
            position: "relative",
            overflow: "hidden"
        }}>
            <div className="glass-card" style={{ width: "100%", maxWidth: "480px", padding: "32px", position: "relative", zIndex: 1 }}>
                <div style={{ textAlign: "center", marginBottom: "32px" }}>
                    <span style={{ fontSize: "40px", display: "block", marginBottom: "16px" }}>
                        {formData.role === "judge" ? "👨‍⚖️" : formData.role === "lawyer" ? "👔" : "👤"}
                    </span>
                    <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }} className="gradient-text">
                        {isLogin ? "Welcome Back" : "Create Account"}
                    </h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0 }}>
                        {isLogin ? "Enter your credentials to access your workspace" : `Set up your ${formData.role} profile`}
                    </p>
                </div>

                {error && (
                    <div style={{ background: "rgba(239,68,68,0.1)", color: "#ef4444", padding: "12px", borderRadius: "8px", fontSize: "14px", marginBottom: "24px", border: "1px solid rgba(239,68,68,0.2)" }}>
                        ⚠️ {error}
                    </div>
                )}

                {/* Tab Switcher */}
                <div style={{ display: "flex", gap: "8px", marginBottom: "24px", background: "rgba(255,255,255,0.05)", padding: "4px", borderRadius: "8px" }}>
                    <button
                        type="button"
                        className="btn-secondary"
                        style={{ flex: 1, background: isLogin ? "var(--bg-card)" : "transparent", border: isLogin ? "1px solid var(--border-color)" : "none" }}
                        onClick={() => { setIsLogin(true); setError("") }}
                    >
                        Login
                    </button>
                    <button
                        type="button"
                        className="btn-secondary"
                        style={{ flex: 1, background: !isLogin ? "var(--bg-card)" : "transparent", border: !isLogin ? "1px solid var(--border-color)" : "none" }}
                        onClick={() => { setIsLogin(false); setError("") }}
                    >
                        Sign Up
                    </button>
                </div>

                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                    {/* Always shown for Login & Reg */}
                    <div className="input-group">
                        <label>Username</label>
                        <input type="text" name="username" className="form-input" required value={formData.username} onChange={handleChange} />
                    </div>
                    <div className="input-group">
                        <label>Password</label>
                        <input type="password" name="password" className="form-input" required value={formData.password} onChange={handleChange} />
                    </div>

                    {/* Registration Only Fields */}
                    {!isLogin && (
                        <>
                            <div className="input-group">
                                <label>Email Address</label>
                                <input type="email" name="email" className="form-input" required value={formData.email} onChange={handleChange} />
                            </div>
                            <div className="input-group">
                                <label>Full Name</label>
                                <input type="text" name="full_name" className="form-input" required value={formData.full_name} onChange={handleChange} />
                            </div>

                            {/* Role-Specific Fields */}
                            {formData.role === "judge" && (
                                <div className="input-group">
                                    <label>Court Name (Assignment)</label>
                                    <input type="text" name="court_name" className="form-input" required placeholder="e.g. Supreme Court of India" value={formData.court_name} onChange={handleChange} />
                                </div>
                            )}

                            {formData.role === "lawyer" && (
                                <>
                                    <div className="input-group">
                                        <label>Bar Council ID</label>
                                        <input type="text" name="bar_council_id" className="form-input" required placeholder="e.g. D/123/2026" value={formData.bar_council_id} onChange={handleChange} />
                                    </div>
                                    <div className="input-group">
                                        <label>Specialization</label>
                                        <input type="text" name="specialization" className="form-input" required placeholder="e.g. Criminal, Corporate" value={formData.specialization} onChange={handleChange} />
                                    </div>
                                    <div className="input-group">
                                        <label>About You</label>
                                        <textarea name="about" className="form-input" rows={3} required placeholder="Brief biography for the public directory..." value={formData.about} onChange={handleChange}></textarea>
                                    </div>
                                </>
                            )}
                        </>
                    )}

                    <button type="submit" className="btn-primary" style={{ width: "100%", marginTop: "8px", padding: "14px" }} disabled={loading}>
                        {loading ? "Processing..." : isLogin ? "Sign In to Workspace →" : "Create Account →"}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default function AuthPage() {
    return (
        <Suspense fallback={<div style={{ padding: "40px", textAlign: "center", color: "white" }}>Loading Secure Portal...</div>}>
            <AuthContent />
        </Suspense>
    )
}
