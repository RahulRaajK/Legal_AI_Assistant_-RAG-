"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";

export default function CaseDashboard() {
    const params = useParams();
    const router = useRouter();
    const caseId = params.id as string;

    const [caseData, setCaseData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("overview");

    const [userRole, setUserRole] = useState("citizen");

    // Evidence Upload State
    const [uploadSide, setUploadSide] = useState("petitioner");
    const [documentType, setDocumentType] = useState("evidence");
    const [uploading, setUploading] = useState(false);

    // AI Analysis State
    const [analyzing, setAnalyzing] = useState(false);

    // Judge Editing State
    const [editingCourtDetails, setEditingCourtDetails] = useState(false);
    const [courtDetails, setCourtDetails] = useState({
        next_hearing_date: "",
        hearing_time: "",
        petitioner_attendance: "",
        respondent_attendance: ""
    });

    const loadCase = async () => {
        try {
            const data = await api.getCase(caseId);
            setCaseData(data);
            setCourtDetails({
                next_hearing_date: data.next_hearing_date || "",
                hearing_time: data.hearing_time || "",
                petitioner_attendance: data.petitioner_attendance || "",
                respondent_attendance: data.respondent_attendance || ""
            });
            setUserRole(localStorage.getItem("user_role") || "citizen");
        } catch (e) {
            console.error(e);
            alert("Error loading case");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (caseId) loadCase();
    }, [caseId]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append("file", file);
        formData.append("case_id", caseId);
        formData.append("submitted_by", uploadSide);
        formData.append("document_type", documentType);

        try {
            // Re-using the raw fetch here to handle FormData easily
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:8000/api/documents/upload", {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` },
                body: formData,
            });

            if (!response.ok) throw new Error("Upload failed");
            await loadCase(); // Refresh case to show new document
            alert("Evidence uploaded successfully!");
        } catch (err: any) {
            alert(err.message);
        } finally {
            setUploading(false);
            e.target.value = ''; // Reset input
        }
    };

    const runAIAnalysis = async () => {
        setAnalyzing(true);
        try {
            await api.analyzeCase(caseId);
            await loadCase(); // Refresh to show AI results
        } catch (e: any) {
            alert(e.message);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleAdmissibility = async (documentId: string, status: string) => {
        try {
            await api.updateAdmissibility(documentId, status);
            await loadCase();
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        }
    };

    const handleSaveCourtDetails = async () => {
        try {
            await api.updateCase(caseId, courtDetails);
            setEditingCourtDetails(false);
            await loadCase();
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        }
    };

    const getBadgeClass = (status: string) => {
        switch (status) {
            case "active": return "badge-active";
            case "pending": return "badge-pending";
            case "urgent": return "badge-urgent";
            default: return "badge-closed";
        }
    };

    if (loading) return <div style={{ textAlign: "center", padding: "100px" }}><div className="spinner" style={{ margin: "0 auto" }} /></div>;
    if (!caseData) return <div style={{ textAlign: "center", padding: "100px" }}>Case not found</div>;

    const petitionerDocs = caseData.documents?.filter((d: any) => d.submitted_by === "petitioner") || [];
    const respondentDocs = caseData.documents?.filter((d: any) => d.submitted_by === "respondent") || [];

    return (
        <div>
            {/* Header Area */}
            <div style={{ marginBottom: "24px" }}>
                <button
                    onClick={() => router.push("/cases")}
                    style={{ background: "none", border: "none", color: "var(--accent-secondary)", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", padding: "0 0 16px 0", fontSize: "14px", fontWeight: 600 }}
                >
                    ← Back to Cases List
                </button>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                        <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }} className="gradient-text">{caseData.case_title}</h1>
                        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap", fontSize: "13px", color: "var(--text-secondary)" }}>
                            <span className={`badge ${getBadgeClass(caseData.status)}`}>{caseData.status}</span>
                            {caseData.case_number && <span>#{caseData.case_number}</span>}
                            {caseData.fir_number && <span style={{ padding: "2px 8px", background: "rgba(255, 69, 58, 0.1)", color: "#ff453a", borderRadius: "12px" }}>FIR: {caseData.fir_number}</span>}
                            <span>{caseData.court_name}</span>
                        </div>
                    </div>
                    {userRole !== 'judge' && caseData.win_probability && (
                        <div className="glass-card" style={{ padding: "12px 20px", textAlign: "center", border: "1px solid rgba(255, 215, 0, 0.3)", background: "rgba(255, 215, 0, 0.05)" }}>
                            <div style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "1px", color: "var(--accent-gold)", marginBottom: "4px", fontWeight: 600 }}>Win Probability</div>
                            <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--text-primary)" }}>{Math.round(caseData.win_probability * 100)}%</div>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation Tabs */}
            <div style={{ display: "flex", gap: "32px", borderBottom: "1px solid var(--border-color)", marginBottom: "24px" }}>
                {["overview", "evidence", "analysis"].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        style={{
                            background: "none", border: "none", padding: "0 0 12px 0", fontSize: "14px", fontWeight: 600, cursor: "pointer", textTransform: "capitalize",
                            color: activeTab === tab ? "var(--text-primary)" : "var(--text-secondary)",
                            borderBottom: activeTab === tab ? "2px solid var(--accent-primary)" : "2px solid transparent",
                            transition: "all 0.2s"
                        }}
                    >
                        {tab === "overview" && "📊 Case Overview"}
                        {tab === "evidence" && "📁 Evidence & Documents"}
                        {tab === "analysis" && "🤖 AI Analysis"}
                    </button>
                ))}
            </div>

            {/* TAB CONTENT: CASE OVERVIEW */}
            {activeTab === "overview" && (
                <div style={{ display: "grid", gap: "24px" }}>
                    {/* Top Grid */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px" }}>
                        {/* Case Details Card */}
                        <div className="glass-card" style={{ padding: "24px" }}>
                            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px", color: "var(--accent-secondary)" }}>Case Details</h3>
                            <div style={{ display: "grid", gridTemplateColumns: "130px 1fr", gap: "12px", fontSize: "13px" }}>
                                <div style={{ color: "var(--text-secondary)" }}>Case Type:</div><div>{caseData.case_type || "-"}</div>
                                <div style={{ color: "var(--text-secondary)" }}>Filing Date:</div><div>{caseData.filing_date ? new Date(caseData.filing_date).toLocaleDateString() : "-"}</div>
                                <div style={{ color: "var(--text-secondary)" }}>Registration No:</div><div>{caseData.registration_number || "-"}</div>
                                <div style={{ color: "var(--text-secondary)" }}>Under Acts:</div><div>{caseData.act || "-"}</div>
                            </div>
                        </div>

                        {/* Court Details Card */}
                        <div className="glass-card" style={{ padding: "24px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                                <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0, color: "var(--accent-secondary)" }}>Status & Court</h3>
                                {userRole === "judge" && !editingCourtDetails && (
                                    <button onClick={() => setEditingCourtDetails(true)} style={{ background: "none", border: "1px solid var(--border-color)", borderRadius: "4px", padding: "4px 8px", fontSize: "11px", color: "var(--text-secondary)", cursor: "pointer" }}>Edit Details</button>
                                )}
                                {userRole === "judge" && editingCourtDetails && (
                                    <div style={{ display: "flex", gap: "8px" }}>
                                        <button onClick={() => setEditingCourtDetails(false)} style={{ background: "none", border: "none", fontSize: "11px", color: "var(--text-secondary)", cursor: "pointer" }}>Cancel</button>
                                        <button onClick={handleSaveCourtDetails} style={{ background: "var(--accent-primary)", border: "none", borderRadius: "4px", padding: "4px 8px", fontSize: "11px", color: "white", cursor: "pointer" }}>Save</button>
                                    </div>
                                )}
                            </div>

                            <div style={{ display: "grid", gridTemplateColumns: "130px 1fr", gap: "12px", fontSize: "13px" }}>
                                <div style={{ color: "var(--text-secondary)" }}>Stage of Case:</div><div>{caseData.status}</div>
                                <div style={{ color: "var(--text-secondary)" }}>Judge:</div><div>{caseData.judge_name || "-"}</div>

                                <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>Next Hearing Date:</div>
                                <div style={{ marginTop: "8px" }}>
                                    {editingCourtDetails ? (
                                        <input type="date" value={courtDetails.next_hearing_date ? courtDetails.next_hearing_date.split('T')[0] : ''} onChange={e => setCourtDetails({ ...courtDetails, next_hearing_date: e.target.value })} className="input-field" style={{ padding: "4px 8px", fontSize: "12px", width: "100%" }} />
                                    ) : (
                                        <span style={{ color: "var(--accent-primary)", fontWeight: 600 }}>{caseData.next_hearing_date ? new Date(caseData.next_hearing_date).toLocaleDateString() : "-"}</span>
                                    )}
                                </div>

                                <div style={{ color: "var(--text-secondary)" }}>Hearing Time:</div>
                                <div>
                                    {editingCourtDetails ? (
                                        <input type="time" value={courtDetails.hearing_time} onChange={e => setCourtDetails({ ...courtDetails, hearing_time: e.target.value })} className="input-field" style={{ padding: "4px 8px", fontSize: "12px", width: "100%" }} />
                                    ) : (
                                        <span>{caseData.hearing_time || "-"}</span>
                                    )}
                                </div>

                                <div style={{ color: "var(--text-secondary)", marginTop: "8px" }}>Pet. Attendance:</div>
                                <div style={{ marginTop: "8px" }}>
                                    {editingCourtDetails ? (
                                        <select value={courtDetails.petitioner_attendance} onChange={e => setCourtDetails({ ...courtDetails, petitioner_attendance: e.target.value })} className="input-field" style={{ padding: "4px 8px", fontSize: "12px", width: "100%" }}>
                                            <option value="">Unknown</option>
                                            <option value="Present">Present</option>
                                            <option value="Absent">Absent</option>
                                        </select>
                                    ) : (
                                        <span>{caseData.petitioner_attendance || "-"}</span>
                                    )}
                                </div>

                                <div style={{ color: "var(--text-secondary)" }}>Res. Attendance:</div>
                                <div>
                                    {editingCourtDetails ? (
                                        <select value={courtDetails.respondent_attendance} onChange={e => setCourtDetails({ ...courtDetails, respondent_attendance: e.target.value })} className="input-field" style={{ padding: "4px 8px", fontSize: "12px", width: "100%" }}>
                                            <option value="">Unknown</option>
                                            <option value="Present">Present</option>
                                            <option value="Absent">Absent</option>
                                        </select>
                                    ) : (
                                        <span>{caseData.respondent_attendance || "-"}</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Parties Section */}
                    <div className="glass-card" style={{ padding: "24px" }}>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 20px", color: "var(--accent-secondary)" }}>Petitioner and Advocate</h3>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                            <div>
                                <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", marginBottom: "4px" }}>Petitioner(s)</div>
                                <div style={{ fontSize: "15px", fontWeight: 600 }}>1. {caseData.petitioner || "-"}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", marginBottom: "4px" }}>Advocate</div>
                                <div style={{ fontSize: "15px", fontWeight: 600 }}>{caseData.advocate_name || "-"}</div>
                            </div>
                        </div>

                        <div style={{ height: "1px", background: "var(--border-color)", margin: "20px 0" }} />

                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 20px", color: "var(--accent-secondary)" }}>Respondent and Advocate</h3>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                            <div>
                                <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", marginBottom: "4px" }}>Respondent(s)</div>
                                <div style={{ fontSize: "15px", fontWeight: 600 }}>1. {caseData.respondent || "-"}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", marginBottom: "4px" }}>Advocate</div>
                                <div style={{ fontSize: "15px", fontWeight: 600 }}>-</div>
                            </div>
                        </div>
                    </div>

                    {/* Facts */}
                    {caseData.facts && (
                        <div className="glass-card" style={{ padding: "24px", borderLeft: "4px solid var(--accent-gold)" }}>
                            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 12px", color: "var(--accent-gold)" }}>Case Facts Summary</h3>
                            <p style={{ margin: 0, fontSize: "14px", lineHeight: 1.6, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>{caseData.facts}</p>
                        </div>
                    )}
                </div>
            )}

            {/* TAB CONTENT: EVIDENCE & DOCUMENTS */}
            {activeTab === "evidence" && (
                <div style={{ display: "grid", gap: "24px" }}>
                    <div className="glass-card" style={{ padding: "24px", background: "linear-gradient(145deg, rgba(10, 132, 255, 0.05), rgba(0,0,0,0))" }}>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>Upload Case Document</h3>
                        <div style={{ display: "flex", gap: "16px", alignItems: "center", flexWrap: "wrap" }}>
                            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Submitted By</label>
                                <select className="input-field" value={uploadSide} onChange={e => setUploadSide(e.target.value)} style={{ padding: "8px 12px", width: "160px" }}>
                                    <option value="petitioner">Petitioner</option>
                                    <option value="respondent">Respondent</option>
                                    <option value="court">Court</option>
                                </select>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Document Type</label>
                                <select className="input-field" value={documentType} onChange={e => setDocumentType(e.target.value)} style={{ padding: "8px 12px", width: "160px" }}>
                                    <option value="evidence">Evidence</option>
                                    <option value="fir">FIR / Police Report</option>
                                    <option value="witness_statement">Witness Statement</option>
                                    <option value="court_order">Court Order</option>
                                </select>
                            </div>

                            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "6px" }}>
                                <label style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Select PDF or Document File</label>
                                <div style={{ position: "relative" }}>
                                    <input
                                        type="file"
                                        accept=".pdf,.txt,.docx"
                                        style={{ position: "absolute", inset: 0, opacity: 0, cursor: "pointer" }}
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                    />
                                    <div className="btn-secondary" style={{ width: "100%", textAlign: "center", background: uploading ? "var(--bg-secondary)" : "rgba(10, 132, 255, 0.1)", border: "1px dashed var(--accent-primary)" }}>
                                        {uploading ? "⏳ Uploading & Processing..." : "📄 Click or Drag & Drop File"}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "24px" }}>
                        {/* Petitioner Docs */}
                        <div className="glass-card" style={{ padding: "24px", borderTop: "4px solid var(--accent-primary)" }}>
                            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px", display: "flex", justifyContent: "space-between" }}>
                                <span>Petitioner Evidence</span>
                                <span className="badge" style={{ background: "rgba(10, 132, 255, 0.1)", color: "var(--accent-primary)" }}>{petitionerDocs.length} files</span>
                            </h3>
                            {petitionerDocs.length === 0 ? (
                                <div style={{ padding: "20px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px", background: "var(--bg-secondary)", borderRadius: "8px" }}>No petitioner documents uploaded yet.</div>
                            ) : (
                                <div style={{ display: "grid", gap: "12px" }}>
                                    {petitionerDocs.map((doc: any) => (
                                        <div key={doc.id} style={{ background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)", overflow: "hidden" }}>
                                            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px" }}>
                                                <div style={{ fontSize: "24px" }}>📄</div>
                                                <div style={{ flex: 1, minWidth: 0 }}>
                                                    <div style={{ fontSize: "13px", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{doc.filename}</div>
                                                    <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "capitalize" }}>{doc.document_type.replace("_", " ")}</div>
                                                </div>
                                                {doc.is_processed === "completed" ? (
                                                    <span style={{ fontSize: "10px", padding: "2px 6px", background: "rgba(48, 209, 88, 0.1)", color: "#30d158", borderRadius: "12px" }}>Parsed by AI</span>
                                                ) : (
                                                    <span style={{ fontSize: "10px", padding: "2px 6px", background: "rgba(255, 159, 10, 0.1)", color: "#ff9f0a", borderRadius: "12px" }}>Parsing...</span>
                                                )}
                                            </div>
                                            <div style={{ padding: "12px", borderTop: "1px solid var(--border-color)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                                <div style={{ fontSize: "11px", display: "flex", alignItems: "center", gap: "6px" }}>
                                                    <span style={{ color: "var(--text-secondary)" }}>Status:</span>
                                                    {doc.admissibility_status === "valid" && <span style={{ color: "#30d158", fontWeight: 600 }}>✅ Admissible</span>}
                                                    {doc.admissibility_status === "invalid" && <span style={{ color: "#ff453a", fontWeight: 600 }}>❌ Inadmissible</span>}
                                                    {(!doc.admissibility_status || doc.admissibility_status === "pending") && <span style={{ color: "#ff9f0a", fontWeight: 600 }}>⏳ Pending Validation</span>}
                                                </div>
                                                {userRole === "judge" && (
                                                    <div style={{ display: "flex", gap: "8px" }}>
                                                        <button onClick={() => handleAdmissibility(doc.id, "valid")} disabled={doc.admissibility_status === "valid"} style={{ border: "1px solid #30d158", background: doc.admissibility_status === "valid" ? "rgba(48, 209, 88, 0.2)" : "transparent", color: "#30d158", borderRadius: "4px", padding: "2px 8px", fontSize: "11px", cursor: "pointer" }}>Mark Valid</button>
                                                        <button onClick={() => handleAdmissibility(doc.id, "invalid")} disabled={doc.admissibility_status === "invalid"} style={{ border: "1px solid #ff453a", background: doc.admissibility_status === "invalid" ? "rgba(255, 69, 58, 0.2)" : "transparent", color: "#ff453a", borderRadius: "4px", padding: "2px 8px", fontSize: "11px", cursor: "pointer" }}>Mark Invalid</button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Respondent Docs */}
                        <div className="glass-card" style={{ padding: "24px", borderTop: "4px solid #ff453a" }}>
                            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px", display: "flex", justifyContent: "space-between" }}>
                                <span>Respondent Evidence</span>
                                <span className="badge" style={{ background: "rgba(255, 69, 58, 0.1)", color: "#ff453a" }}>{respondentDocs.length} files</span>
                            </h3>
                            {respondentDocs.length === 0 ? (
                                <div style={{ padding: "20px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px", background: "var(--bg-secondary)", borderRadius: "8px" }}>No respondent documents uploaded yet.</div>
                            ) : (
                                <div style={{ display: "grid", gap: "12px" }}>
                                    {respondentDocs.map((doc: any) => (
                                        <div key={doc.id} style={{ background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)", overflow: "hidden" }}>
                                            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px" }}>
                                                <div style={{ fontSize: "24px" }}>📄</div>
                                                <div style={{ flex: 1, minWidth: 0 }}>
                                                    <div style={{ fontSize: "13px", fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{doc.filename}</div>
                                                    <div style={{ fontSize: "11px", color: "var(--text-secondary)", textTransform: "capitalize" }}>{doc.document_type.replace("_", " ")}</div>
                                                </div>
                                                {doc.is_processed === "completed" ? (
                                                    <span style={{ fontSize: "10px", padding: "2px 6px", background: "rgba(48, 209, 88, 0.1)", color: "#30d158", borderRadius: "12px" }}>Parsed by AI</span>
                                                ) : (
                                                    <span style={{ fontSize: "10px", padding: "2px 6px", background: "rgba(255, 159, 10, 0.1)", color: "#ff9f0a", borderRadius: "12px" }}>Parsing...</span>
                                                )}
                                            </div>
                                            <div style={{ padding: "12px", borderTop: "1px solid var(--border-color)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                                <div style={{ fontSize: "11px", display: "flex", alignItems: "center", gap: "6px" }}>
                                                    <span style={{ color: "var(--text-secondary)" }}>Status:</span>
                                                    {doc.admissibility_status === "valid" && <span style={{ color: "#30d158", fontWeight: 600 }}>✅ Admissible</span>}
                                                    {doc.admissibility_status === "invalid" && <span style={{ color: "#ff453a", fontWeight: 600 }}>❌ Inadmissible</span>}
                                                    {(!doc.admissibility_status || doc.admissibility_status === "pending") && <span style={{ color: "#ff9f0a", fontWeight: 600 }}>⏳ Pending Validation</span>}
                                                </div>
                                                {userRole === "judge" && (
                                                    <div style={{ display: "flex", gap: "8px" }}>
                                                        <button onClick={() => handleAdmissibility(doc.id, "valid")} disabled={doc.admissibility_status === "valid"} style={{ border: "1px solid #30d158", background: doc.admissibility_status === "valid" ? "rgba(48, 209, 88, 0.2)" : "transparent", color: "#30d158", borderRadius: "4px", padding: "2px 8px", fontSize: "11px", cursor: "pointer" }}>Mark Valid</button>
                                                        <button onClick={() => handleAdmissibility(doc.id, "invalid")} disabled={doc.admissibility_status === "invalid"} style={{ border: "1px solid #ff453a", background: doc.admissibility_status === "invalid" ? "rgba(255, 69, 58, 0.2)" : "transparent", color: "#ff453a", borderRadius: "4px", padding: "2px 8px", fontSize: "11px", cursor: "pointer" }}>Mark Invalid</button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* TAB CONTENT: AI ANALYSIS */}
            {activeTab === "analysis" && (
                <div style={{ display: "grid", gap: "24px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(10, 132, 255, 0.05)", border: "1px solid rgba(10, 132, 255, 0.2)", padding: "24px", borderRadius: "16px" }}>
                        <div>
                            <h3 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 8px", color: "var(--accent-primary)" }}>DeepSeek Cross-Examination AI</h3>
                            <p style={{ margin: 0, fontSize: "13px", color: "var(--text-secondary)" }}>The AI will read the case facts and <strong>all uploaded evidence PDFs</strong> from both sides to generate a comprehensive prediction and argument list.</p>
                        </div>
                        <button className="btn-primary" onClick={runAIAnalysis} disabled={analyzing} style={{ padding: "12px 24px", minWidth: "200px" }}>
                            {analyzing ? <><div className="spinner" style={{ width: "16px", height: "16px", marginRight: "8px", display: "inline-block" }} /> Analyzing...</> : "🚀 Run Deep Analysis"}
                        </button>
                    </div>

                    {caseData.ai_summary && (
                        <div className="glass-card" style={{ padding: "24px" }}>
                            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px", display: "flex", alignItems: "center", gap: "8px" }}>
                                ⚖️ Objective Case Analysis
                            </h3>
                            <div style={{ fontSize: "14px", lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                                {caseData.ai_summary}
                            </div>
                        </div>
                    )}

                    {caseData.ai_arguments && (
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "24px" }}>
                            <div className="glass-card" style={{ padding: "24px", borderTop: "4px solid var(--accent-primary)" }}>
                                <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>🛡️ Petitioner Arguments (Generated)</h3>
                                <div style={{ fontSize: "14px", lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                                    {caseData.ai_arguments.petitioner || "Run analysis to generate arguments."}
                                </div>
                            </div>

                            <div className="glass-card" style={{ padding: "24px", borderTop: "4px solid #ff453a" }}>
                                <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>⚔️ Respondent Arguments (Generated)</h3>
                                <div style={{ fontSize: "14px", lineHeight: 1.8, color: "var(--text-secondary)", whiteSpace: "pre-wrap" }}>
                                    {caseData.ai_arguments.respondent || "Run analysis to generate arguments."}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
