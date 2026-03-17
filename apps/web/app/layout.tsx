import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TestGen",
  description: "Generate end-to-end Playwright test scripts from plain-English requirements.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <header style={s.header}>
          <span style={s.wordmark}>TestGen</span>
          <span style={s.badge}>beta</span>
        </header>

        <main style={s.main}>{children}</main>
      </body>
    </html>
  );
}

const s: Record<string, React.CSSProperties> = {
  header: {
    display: "flex",
    alignItems: "center",
    gap: "0.6rem",
    padding: "0 2rem",
    height: "52px",
    borderBottom: "1px solid var(--border)",
    background: "var(--surface)",
    flexShrink: 0,
  },
  wordmark: {
    fontWeight: 700,
    fontSize: "0.95rem",
    letterSpacing: "-0.02em",
    color: "var(--text)",
  },
  badge: {
    fontSize: "0.65rem",
    fontWeight: 600,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: "var(--text-3)",
    border: "1px solid var(--border-2)",
    borderRadius: "var(--radius-sm)",
    padding: "0.1rem 0.4rem",
  },
  main: {
    flex: 1,
    maxWidth: "760px",
    width: "100%",
    margin: "0 auto",
    padding: "2.5rem 1.5rem 4rem",
  },
};
