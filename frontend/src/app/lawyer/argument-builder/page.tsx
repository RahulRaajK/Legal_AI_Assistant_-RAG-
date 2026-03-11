"use client";
import { useState, useRef } from "react";
import api from "@/lib/api";

export default function ArgumentBuilder() {
    const [file, setFile] = useState<File | null>(null);
    const [side, setSide] = useState("petitioner");
    const [context, setContext] = useState("");
    const [loading, setLoading] = useState(false);
    const [statusText, setStatusText] = useState("");
    const [argumentsResult, setArgumentsResult] = useState("");

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const handeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file && !context.trim()) {
            alert("Please upload a document or provide case context.");
            return;
        }

        setLoading(true);
        setStatusText("Uploading document...");
        setArgumentsResult("");

        try {
            let docId = "general";
            if (file) {
                const uploadRes = await api.uploadDocument(file, "argument_builder", "evidence");
                docId = uploadRes.id;
            }

            setStatusText("Generating arguments with DeepSeek-V3...");
            const result = await api.buildArguments(docId, side, context);
            setArgumentsResult(result.arguments);

        } catch (err: any) {
            console.error(err);
            alert(`Error generating arguments: ${err.message || 'Unknown error'}`);
        } finally {
            setLoading(false);
            setStatusText("");
        }
    };

    return (
        <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
            <div style={{ marginBottom: "32px" }}>
                <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }}>
                    🧠 <span className="gradient-text">Advanced AI Argument Builder</span>
                </h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                    Upload evidence documents and generate court-ready legal arguments referencing past precedents.
                </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "350px 1fr", gap: "24px", alignItems: "start" }}>
                {/* Input Form */}
                <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "20px" }}>
                    <div>
                        <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
                            Representing Side
                        </label>
                        <select
                            className="form-input"
                            value={side}
                            onChange={(e) => setSide(e.target.value)}
                            disabled={loading}
                        >
                            <option value="petitioner">Petitioner / Plaintiff</option>
                            <option value="respondent">Respondent / Defendant</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
                            Upload Evidence or Brief (Optional if Context provided)
                        </label>
                        <div
                            style={{
                                border: "2px dashed var(--border-color)", borderRadius: "8px", padding: "24px",
                                textAlign: "center", cursor: loading ? "default" : "pointer",
                                background: file ? "rgba(99,102,241,0.05)" : "transparent"
                            }}
                            onClick={() => !loading && fileInputRef.current?.click()}
                        >
                            <input
                                type="file"
                                ref={fileInputRef}
                                style={{ display: "none" }}
                                accept=".pdf,.txt,.docx"
                                onChange={handleFileChange}
                                disabled={loading}
                            />
                            <span style={{ fontSize: "24px", display: "block", marginBottom: "8px" }}>📄</span>
                            <div style={{ fontSize: "14px", color: file ? "#818cf8" : "var(--text-secondary)", fontWeight: file ? 600 : 400 }}>
                                {file ? file.name : "Click to select file (.pdf, .txt, .docx)"}
                            </div>
                        </div>
                        {file && (
                            <button
                                onClick={() => setFile(null)}
                                style={{ background: "transparent", color: "#ef4444", border: "none", fontSize: "12px", marginTop: "8px", cursor: "pointer", padding: 0 }}
                                disabled={loading}
                            >
                                Remove File
                            </button>
                        )}
                    </div>

                    <div>
                        <label style={{ display: "block", fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
                            Case Context & Notes
                        </label>
                        <textarea
                            className="form-input"
                            rows={6}
                            placeholder="E.g., Client is accused under IPC 302, but claims alibi. Provide any specific angles to focus on..."
                            value={context}
                            onChange={(e) => setContext(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <button
                        className="btn-primary"
                        onClick={handeSubmit}
                        disabled={loading || (!file && !context.trim())}
                        style={{ padding: "12px", fontSize: "15px", fontWeight: 600 }}
                    >
                        {loading ? statusText || "Processing..." : "Generate Arguments"}
                    </button>
                </div>

                {/* Results Panel */}
                <div className="glass-card" style={{ padding: "32px", height: "100%", display: "flex", flexDirection: "column" }}>
                    <h2 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 16px" }}>Generated Strategy</h2>

                    <div style={{
                        flex: 1,
                        background: "var(--bg-card)",
                        borderRadius: "12px",
                        border: "1px solid var(--border-color)",
                        padding: "24px",
                        overflowY: "auto",
                        minHeight: "400px",
                        fontSize: "15px",
                        lineHeight: 1.6
                    }}>
                        {!argumentsResult ? (
                            <div style={{ color: "var(--text-secondary)", textAlign: "center", paddingTop: "100px" }}>
                                {loading ? (
                                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>
                                        <div style={{ fontSize: "32px" }} className="animate-pulse">🤖</div>
                                        <div className="gradient-text" style={{ fontWeight: 600 }}>{statusText}</div>
                                    </div>
                                ) : (
                                    "Fill out the parameters and click Generate Arguments to see AI suggestions."
                                )}
                            </div>
                        ) : (
                            <div style={{ whiteSpace: "pre-wrap" }}>
                                {argumentsResult}
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
