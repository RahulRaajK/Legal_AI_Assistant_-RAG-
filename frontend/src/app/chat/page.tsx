"use client";
import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: any[];
    intents?: string[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [role, setRole] = useState("citizen");
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const saved = localStorage.getItem("user_role");
        if (saved) setRole(saved);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;
        const userMessage = input.trim();
        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
        setLoading(true);

        try {
            const response = await api.sendMessage(userMessage, sessionId || undefined, role);
            setSessionId(response.session_id);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: response.message,
                    sources: response.sources,
                    intents: response.intents,
                },
            ]);
        } catch (error: any) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: `⚠️ Error: ${error.message}. Make sure the backend is running on http://localhost:8000` },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const formatMarkdown = (text: string) => {
        // Simple markdown rendering
        let html = text
            .replace(/### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^- (.*?)$/gm, '<li>$1</li>')
            .replace(/^\d+\.\s(.*?)$/gm, '<li>$1</li>')
            .replace(/\n\n/g, '<br/><br/>')
            .replace(/\n/g, '<br/>');

        // Wrap consecutive li items in ul
        html = html.replace(/(<li>.*?<\/li>(\s*<br\/>)?)+/g, (match) => `<ul>${match}</ul>`);

        // Handle tables
        html = html.replace(/\|(.+)\|/g, (match) => {
            const cells = match.split('|').filter(c => c.trim());
            if (cells.some(c => c.trim().match(/^-+$/))) return '';
            const tag = cells.some(c => c.trim().match(/^[A-Z]/)) ? 'td' : 'td';
            return '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
        });

        return html;
    };

    const suggestions = role === "judge"
        ? ["Relevant precedents for Article 21 cases", "Summary of Bharatiya Nyaya Sanhita 2023", "What is the basic structure doctrine?"]
        : role === "lawyer"
            ? ["Arguments for breach of contract case", "Cases related to Section 498A IPC", "Motor Vehicles Act compensation precedents"]
            : ["What are my rights if arrested?", "How to file a consumer complaint?", "What does Article 21 mean in simple words?"];

    return (
        <div className="chat-container">
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div>
                    <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 4px" }} className="gradient-text">
                        AI Legal Assistant
                    </h1>
                    <p style={{ color: "var(--text-secondary)", fontSize: "13px", margin: 0 }}>
                        {role === "judge" ? "⚖️ Judge Mode" : role === "lawyer" ? "👔 Lawyer Mode" : "👤 Citizen Mode"} — Ask anything about Indian law
                    </p>
                </div>
                {sessionId && (
                    <button className="btn-secondary" onClick={() => { setMessages([]); setSessionId(null); }}>
                        + New Chat
                    </button>
                )}
            </div>

            {/* Messages */}
            <div className="chat-messages">
                {messages.length === 0 && (
                    <div style={{ textAlign: "center", padding: "60px 20px" }}>
                        <span style={{ fontSize: "64px", display: "block", marginBottom: "16px" }}>⚖️</span>
                        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }} className="gradient-text">
                            Welcome to Legal AI Assistant
                        </h2>
                        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "24px", maxWidth: "500px", margin: "0 auto 24px" }}>
                            I can help you understand Indian laws, find case precedents, analyze documents, and provide legal reasoning.
                        </p>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center" }}>
                            {suggestions.map((s) => (
                                <button
                                    key={s}
                                    className="btn-secondary"
                                    style={{ fontSize: "13px", padding: "8px 16px" }}
                                    onClick={() => { setInput(s); }}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", animation: "fadeIn 0.3s ease" }}>
                        <div className={`message-bubble ${msg.role}`}>
                            <div dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.content) }} />
                            {msg.sources && msg.sources.length > 0 && (
                                <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--border-color)" }}>
                                    <p style={{ fontSize: "11px", color: "var(--accent-gold)", fontWeight: 600, marginBottom: "6px" }}>📚 Sources:</p>
                                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                                        {msg.sources.map((s: any, j: number) => (
                                            <span key={j} style={{
                                                fontSize: "11px", padding: "3px 8px", borderRadius: "6px",
                                                background: "rgba(99, 102, 241, 0.15)", color: "var(--accent-secondary)"
                                            }}>
                                                {s.act_name} {s.section ? `§${s.section}` : ""}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 0" }}>
                        <div className="spinner" />
                        <span style={{ color: "var(--text-secondary)", fontSize: "13px" }}>Analyzing your legal query...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="chat-input-area">
                <div style={{ display: "flex", gap: "12px" }}>
                    <input
                        className="input-field"
                        placeholder={
                            role === "judge" ? "Ask about laws, precedents, or case analysis..."
                                : role === "lawyer" ? "Search statutes, find arguments, analyze cases..."
                                    : "Ask any legal question in simple language..."
                        }
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        disabled={loading}
                    />
                    <button className="btn-primary" onClick={sendMessage} disabled={loading || !input.trim()}>
                        {loading ? <><div className="spinner" style={{ width: "16px", height: "16px" }} /> Thinking...</> : "Send ➤"}
                    </button>
                </div>
            </div>
        </div>
    );
}
