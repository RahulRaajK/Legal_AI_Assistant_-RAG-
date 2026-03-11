"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import "./globals.css";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: "🏛️", roles: ["judge", "lawyer", "citizen"] },
  { href: "/judge/calendar", label: "Court Calendar", icon: "📅", roles: ["judge"] },
  { href: "/lawyer/argument-builder", label: "Argument AI", icon: "🧠", roles: ["lawyer"] },
  { href: "/lawyer/profile", label: "Lawyer Profile", icon: "👔", roles: ["lawyer"] },
  { href: "/citizen/incident-ai", label: "Incident AI", icon: "🚨", roles: ["citizen"] },
  { href: "/citizen/directory", label: "Lawyer Directory", icon: "💼", roles: ["citizen"] },
  { href: "/chat", label: "AI Assistant", icon: "🤖", roles: ["judge", "lawyer", "citizen"] },
  { href: "/cases", label: "Case Management", icon: "📂", roles: ["judge", "lawyer", "citizen"] },
  { href: "/search", label: "Legal Search", icon: "🔍", roles: ["judge", "lawyer", "citizen"] },
  { href: "/documents", label: "Documents", icon: "📄", roles: ["judge", "lawyer", "citizen"] },
  { href: "/crawler", label: "Law Updates", icon: "🌐", roles: ["judge", "lawyer", "citizen"] },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState("citizen");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  const isPublicRoute = pathname === "/" || pathname?.startsWith("/auth");

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    const savedRole = localStorage.getItem("user_role");

    if (token && savedRole) {
      setRole(savedRole);
      setIsAuthenticated(true);
      if (isPublicRoute) {
        router.push("/dashboard");
      }
    } else {
      setIsAuthenticated(false);
      if (!isPublicRoute) {
        router.push("/");
      }
    }
  }, [pathname, router]);

  const handleSignOut = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_role");
    setIsAuthenticated(false);
    router.push("/");
  };

  // Only render children until auth status is known to prevent hydration flash
  if (isAuthenticated === null) return <html lang="en"><body><div className="main-content" style={{ padding: "40px", textAlign: "center", color: "white" }}>Loading Secure Portal...</div></body></html>;

  if (isPublicRoute) {
    return (
      <html lang="en">
        <head>
          <title>Legal AI Assistant — Indian Law</title>
          <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
        </head>
        <body>{children}</body>
      </html>
    );
  }

  return (
    <html lang="en">
      <head>
        <title>Legal AI Assistant — Indian Law</title>
        <meta name="description" content="AI-powered legal assistant for Indian law." />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body>
        <button
          className="fixed top-4 left-4 z-50 p-2 rounded-lg md:hidden"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)" }}
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          ☰
        </button>

        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
          <div style={{ padding: "24px 20px 16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "4px" }}>
              <span style={{ fontSize: "28px" }}>⚖️</span>
              <div>
                <h1 style={{ fontSize: "16px", fontWeight: 800, margin: 0 }} className="gradient-text">
                  Legal AI
                </h1>
                <p style={{ fontSize: "11px", color: "var(--text-secondary)", margin: 0, textTransform: "capitalize" }}>
                  Workspace: {role}
                </p>
              </div>
            </div>
          </div>

          <div style={{ height: "1px", background: "var(--border-color)", margin: "0 16px" }} />

          {/* Navigation */}
          <nav style={{ padding: "12px 0", flex: 1 }}>
            {navItems.filter(item => {
              if (role === "citizen" && item.href === "/documents") {
                return false;
              }
              if (role === "lawyer" && item.href === "/crawler") {
                // optionally hide things for lawyers, but currently they see all.
                return item.roles.includes("lawyer");
              }
              return item.roles.includes(role);
            }).map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`sidebar-link ${pathname === item.href ? "active" : ""}`}
                onClick={() => setSidebarOpen(false)}
              >
                <span style={{ fontSize: "18px" }}>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>

          <div style={{ height: "1px", background: "var(--border-color)", margin: "8px 16px" }} />

          {/* Footer & Logout */}
          <div style={{ padding: "16px 20px" }}>
            <button
              onClick={handleSignOut}
              className="btn-secondary"
              style={{ width: "100%", padding: "8px", fontSize: "13px", marginBottom: "16px" }}
            >
              Sign Out
            </button>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
              <p style={{ margin: 0 }}>📚 Secure Law Portal</p>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {children}
        </main>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 30 }}
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </body>
    </html>
  );
}
