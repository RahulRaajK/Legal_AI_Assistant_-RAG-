"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<any[]>([]);
    const [uploading, setUploading] = useState(false);
    const [analyzing, setAnalyzing] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<any>(null);
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(true);

    const loadDocuments = async () => {
        try {
            const data = await api.getDocuments();
            setDocuments(data);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { loadDocuments(); }, []);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setUploading(true);
        try {
            await api.uploadDocument(file);
            loadDocuments();
        } catch (err: any) { alert(err.message); }
        finally { setUploading(false); }
    };

    const analyzeDoc = async (docId: string) => {
        setAnalyzing(docId);
        try {
            const result = await api.analyzeDocument(docId, question || undefined);
            setAnalysis(result);
        } catch (err: any) { alert(err.message); }
        finally { setAnalyzing(null); }
    };

    const formatSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div>
            <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 4px" }} className="gradient-text">Document Manager</h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginBottom: "24px" }}>
                Upload PDFs, FIRs, contracts, court filings — analyze with AI
            </p>

            {/* Upload Area */}
            <label className="upload-area" style={{ display: "block", marginBottom: "24px" }}>
                <input type="file" accept=".pdf,.txt,.docx,.doc" onChange={handleUpload} style={{ display: "none" }} />
                {uploading ? (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "12px" }}>
                        <div className="spinner" />
                        <span style={{ color: "var(--text-secondary)" }}>Uploading & processing...</span>
                    </div>
                ) : (
                    <>
                        <span style={{ fontSize: "48px", display: "block", marginBottom: "12px" }}>📤</span>
                        <p style={{ fontSize: "15px", fontWeight: 600, margin: "0 0 4px" }}>Drop or click to upload</p>
                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>PDF, DOCX, TXT — Max 50MB</p>
                    </>
                )}
            </label>

            {/* Document List */}
            <div style={{ display: "grid", gridTemplateColumns: analysis ? "1fr 1fr" : "1fr", gap: "20px" }}>
                <div>
                    <h2 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "12px" }}>📁 Uploaded Documents ({documents.length})</h2>
                    {loading ? (
                        <div style={{ textAlign: "center", padding: "40px" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>
                    ) : documents.length === 0 ? (
                        <div className="glass-card" style={{ padding: "32px", textAlign: "center" }}>
                            <p style={{ color: "var(--text-secondary)" }}>No documents uploaded yet.</p>
                        </div>
                    ) : (
                        documents.map((doc) => (
                            <div key={doc.id} className="search-result">
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                                    <div>
                                        <h3 style={{ fontSize: "14px", fontWeight: 600, margin: "0 0 4px" }}>📄 {doc.filename}</h3>
                                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", margin: 0 }}>
                                            {formatSize(doc.file_size)} • {doc.chunk_count} chunks • {new Date(doc.uploaded_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div style={{ display: "flex", gap: "6px" }}>
                                        <span className={`badge ${doc.is_processed === "completed" ? "badge-active" : "badge-pending"}`}>
                                            {doc.is_processed}
                                        </span>
                                        <button
                                            className="btn-secondary"
                                            style={{ padding: "4px 12px", fontSize: "12px" }}
                                            onClick={() => analyzeDoc(doc.id)}
                                            disabled={analyzing === doc.id}
                                        >
                                            {analyzing === doc.id ? "..." : "🤖 Analyze"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Analysis Panel */}
                {analysis && (
                    <div className="glass-card" style={{ padding: "24px", maxHeight: "70vh", overflowY: "auto" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px" }}>
                            <h2 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>🤖 Document Analysis</h2>
                            <button className="btn-secondary" style={{ padding: "4px 10px", fontSize: "12px" }} onClick={() => setAnalysis(null)}>✕</button>
                        </div>
                        <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "12px" }}>
                            📄 {analysis.filename}
                        </p>

                        {/* Ask a question */}
                        <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
                            <input
                                className="input-field"
                                placeholder="Ask a question about this document..."
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                onKeyDown={(e) => { if (e.key === "Enter" && analysis.document_id) analyzeDoc(analysis.document_id); }}
                                style={{ fontSize: "13px" }}
                            />
                        </div>

                        <div style={{ fontSize: "13px", lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                            {analysis.analysis?.analysis || analysis.analysis?.facts || JSON.stringify(analysis.analysis, null, 2)}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
