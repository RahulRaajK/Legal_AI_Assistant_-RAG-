"use client";
import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
}

export default function IncidentAI() {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "Hello. I am the Citizen Incident AI. Describe your situation or legal issue in plain English (or upload a document), and I will help you identify what legal sections apply and what your next steps should be." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput("");
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setLoading(true);

        try {
            // We leverage the existing chat agent, but since the user is logged in as "citizen",
            // the backend Chat system will automatically use the Citizen prompt persona.
            const response = await api.sendMessage(userMessage, undefined, "citizen");

            setMessages(prev => [...prev, {
                role: "assistant",
                content: response.response
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I encountered an error processing your request. Please try again."
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setLoading(true);
        setMessages(prev => [...prev, { role: "user", content: `📎 Uploaded Document: ${file.name}` }]);

        try {
            await api.uploadDocument(file, undefined, "incident_evidence");
            setMessages(prev => [...prev, {
                role: "assistant",
                content: `I have received and securely stored "${file.name}". How is this document related to your incident? Provide any additional context so I can analyze it against the relevant laws.`
            }]);
        } catch (error) {
            console.error("Upload error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I couldn't process that document. Please try a different file or paste the text directly."
            }]);
        } finally {
            setLoading(false);
            if (e.target) e.target.value = ''; // reset
        }
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 80px)" }}>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }}>
                    🚨 <span className="gradient-text">Incident Assistance AI</span>
                </h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                    Explain your problem. Fast, free, and strictly confidential AI guidance.
                </p>
            </div>

            <div className="glass-card" style={{ flex: 1, display: "flex", flexDirection: "column", padding: 0, overflow: "hidden" }}>
                {/* Messages Buffer */}
                <div style={{ flex: 1, overflowY: "auto", padding: "24px", display: "flex", flexDirection: "column", gap: "24px" }}>
                    {messages.map((msg, i) => (
                        <div key={i} style={{ display: "flex", gap: "16px", flexDirection: msg.role === "user" ? "row-reverse" : "row" }}>
                            <div style={{
                                width: "40px", height: "40px", borderRadius: "12px", flexShrink: 0,
                                background: msg.role === "user" ? "var(--bg-card)" : "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))",
                                display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px",
                                border: "1px solid var(--border-color)"
                            }}>
                                {msg.role === "user" ? "👤" : "🤖"}
                            </div>

                            <div style={{
                                maxWidth: "80%", padding: "16px", borderRadius: "12px", lineHeight: 1.6,
                                background: msg.role === "user" ? "linear-gradient(135deg, rgba(99,102,241,0.1), transparent)" : "var(--bg-card)",
                                border: "1px solid var(--border-color)",
                                borderTopRightRadius: msg.role === "user" ? 0 : "12px",
                                borderTopLeftRadius: msg.role === "assistant" ? 0 : "12px",
                            }}>
                                <div style={{ whiteSpace: "pre-wrap", fontSize: "14px" }}>{msg.content}</div>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div style={{ display: "flex", gap: "16px" }}>
                            <div style={{
                                width: "40px", height: "40px", borderRadius: "12px", flexShrink: 0,
                                background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))",
                                display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px"
                            }}>
                                🤖
                            </div>
                            <div style={{ padding: "16px", borderRadius: "12px", background: "var(--bg-card)", border: "1px solid var(--border-color)", color: "var(--text-secondary)" }}>
                                Analyzing incident details...
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Dock */}
                <div style={{ padding: "24px", borderTop: "1px solid var(--border-color)", background: "rgba(15,23,42,0.8)" }}>
                    <form onSubmit={handleSend} style={{ display: "flex", gap: "12px", position: "relative" }}>
                        <input
                            type="file"
                            id="incident-upload"
                            style={{ display: "none" }}
                            onChange={handleFileUpload}
                            disabled={loading}
                            accept=".txt,.pdf,.png,.jpg"
                        />
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={() => document.getElementById("incident-upload")?.click()}
                            disabled={loading}
                            style={{ width: "48px", padding: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px" }}
                            title="Upload Document"
                        >
                            📎
                        </button>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="E.g., My landlord locked me out of my apartment without notice..."
                            className="form-input"
                            style={{ flex: 1, padding: "16px", fontSize: "15px" }}
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={!input.trim() || loading}
                            style={{ width: "100px", fontWeight: "bold" }}
                        >
                            Analyze
                        </button>
                    </form>
                    <div style={{ fontSize: "11px", color: "var(--text-secondary)", textAlign: "center", marginTop: "12px" }}>
                        This assistant provides legal information, not formal legal advice. For representation, please visit the Lawyer Directory.
                    </div>
                </div>
            </div>
        </div>
    );
}
