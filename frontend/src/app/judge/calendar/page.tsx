"use client";
import { useState, useEffect } from "react";
import api from "@/lib/api";

export default function CourtCalendar() {
    const [holidays, setHolidays] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [cases, setCases] = useState<any[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [hData, cData] = await Promise.all([
                    api.getHolidays(),
                    api.getCases().catch(() => [])
                ]);
                setHolidays(hData);
                setCases(cData.filter((c: any) => c.next_hearing_date && new Date(c.next_hearing_date) >= new Date()).slice(0, 5));
            } catch (err) {
                console.error("Failed to load calendar data", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getDaysInMonth = (year: number, month: number) => {
        return new Date(year, month + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (year: number, month: number) => {
        return new Date(year, month, 1).getDay();
    };

    // Currently fixed to March 2026 for demonstration
    const year = 2026;
    const month = 2; // 0-indexed March

    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
    const blanks = Array.from({ length: firstDay }, (_, i) => i);

    const getDayStatus = (dayNum: number) => {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
        const holiday = holidays.find(h => h.holiday_date === dateStr);

        // Sundays are naturally non-working
        const dayOfWeek = new Date(year, month, dayNum).getDay();
        if (dayOfWeek === 0) return { type: "weekend", desc: "Sunday" };

        if (holiday) {
            return { type: holiday.is_working_day ? "working_special" : "holiday", desc: holiday.description };
        }

        return { type: "working", desc: "Working Day" };
    };

    return (
        <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
            <div style={{ marginBottom: "32px" }}>
                <h1 style={{ fontSize: "28px", fontWeight: 800, margin: "0 0 8px" }}>
                    📅 <span className="gradient-text">Court Calendar</span>
                </h1>
                <p style={{ color: "var(--text-secondary)", fontSize: "15px", margin: 0 }}>
                    View official court schedule, holidays, and available hearing dates to avoid scheduling conflicts.
                </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: "24px", alignItems: "start" }}>

                {/* Calendar View */}
                <div className="glass-card" style={{ padding: "24px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
                        <h2 style={{ fontSize: "20px", fontWeight: 700, margin: 0 }}>March 2026</h2>
                        <div style={{ display: "flex", gap: "8px" }}>
                            <button className="btn-secondary" style={{ padding: "4px 12px" }}>&lt;</button>
                            <button className="btn-secondary" style={{ padding: "4px 12px" }}>&gt;</button>
                        </div>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "8px", textAlign: "center", marginBottom: "8px" }}>
                        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
                            <div key={d} style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", padding: "8px 0" }}>{d}</div>
                        ))}
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "8px" }}>
                        {blanks.map(b => <div key={`blank-${b}`} style={{ minHeight: "80px", borderRadius: "8px", background: "rgba(255,255,255,0.02)" }} />)}

                        {days.map(dayNum => {
                            const status = getDayStatus(dayNum);
                            let bg = "var(--bg-card)";
                            let border = "1px solid var(--border-color)";
                            let color = "inherit";

                            if (status.type === "weekend" || status.type === "holiday") {
                                bg = "rgba(239, 68, 68, 0.05)";
                                border = "1px solid rgba(239, 68, 68, 0.2)";
                                color = "#f87171";
                            }

                            return (
                                <div key={dayNum} style={{
                                    minHeight: "80px", borderRadius: "8px", background: bg, border,
                                    padding: "8px", display: "flex", flexDirection: "column", opacity: loading ? 0.5 : 1
                                }}>
                                    <div style={{ fontWeight: 600, color, marginBottom: "4px" }}>{dayNum}</div>
                                    {status.type !== "working" && (
                                        <div style={{ fontSize: "10px", color: "var(--text-secondary)", lineHeight: 1.2 }}>
                                            {status.desc}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Legend & Upcoming */}
                <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                    <div className="glass-card" style={{ padding: "24px" }}>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>Legend</h3>
                        <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontSize: "13px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <div style={{ width: "16px", height: "16px", borderRadius: "4px", background: "var(--bg-card)", border: "1px solid var(--border-color)" }} />
                                <span>Working Day</span>
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <div style={{ width: "16px", height: "16px", borderRadius: "4px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)" }} />
                                <span>Court Holiday / Sunday</span>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card" style={{ padding: "24px" }}>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>Upcoming Holidays</h3>
                        {loading ? <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Loading...</div> : (
                            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                                {holidays.filter(h => !h.is_working_day).slice(0, 5).map((h, i) => (
                                    <div key={i} style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                                        <div style={{ fontWeight: 600, fontSize: "13px", color: "#f87171", width: "80px" }}>
                                            {new Date(h.holiday_date).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                                        </div>
                                        <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{h.description}</div>
                                    </div>
                                ))}
                                {holidays.length === 0 && <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>No upcoming holidays.</div>}
                            </div>
                        )}
                    </div>
                    {/* Upcoming Hearings */}
                    <div className="glass-card" style={{ padding: "24px" }}>
                        <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 16px" }}>Upcoming Hearings</h3>
                        {loading ? <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Loading...</div> : (
                            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                                {cases.map((c, i) => (
                                    <div key={i} style={{ display: "flex", gap: "12px", alignItems: "center", borderBottom: i < cases.length - 1 ? "1px solid var(--border-color)" : "none", paddingBottom: i < cases.length - 1 ? "8px" : 0 }}>
                                        <div style={{ fontWeight: 600, fontSize: "13px", color: "#6366f1", width: "80px" }}>
                                            {new Date(c.next_hearing_date).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                                        </div>
                                        <div style={{ display: "flex", flexDirection: "column" }}>
                                            <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>{c.case_title}</div>
                                            <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>{c.case_number} • {c.hearing_time || "TBD"}</div>
                                        </div>
                                    </div>
                                ))}
                                {cases.length === 0 && <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>No upcoming hearings.</div>}
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
