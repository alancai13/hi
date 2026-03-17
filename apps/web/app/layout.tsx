import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TestGen — E2E Test Script Generator",
  description:
    "Generate Playwright end-to-end test scripts from plain-English requirements.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <header style={styles.header}>
          <span style={styles.logo}>TestGen</span>
          <span style={styles.tagline}>E2E Test Script Generator</span>
        </header>
        <main style={styles.main}>{children}</main>
        <footer style={styles.footer}>
          <span style={{ color: "var(--color-text-muted)", fontSize: "0.8rem" }}>
            Skeleton — not production ready
          </span>
        </footer>
      </body>
    </html>
  );
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "1rem 2rem",
    borderBottom: "1px solid var(--color-border)",
    background: "var(--color-surface)",
  },
  logo: {
    fontWeight: 700,
    fontSize: "1.1rem",
    color: "var(--color-accent)",
    letterSpacing: "-0.02em",
  },
  tagline: {
    fontSize: "0.85rem",
    color: "var(--color-text-muted)",
  },
  main: {
    maxWidth: "900px",
    margin: "0 auto",
    padding: "2rem 1.5rem",
  },
  footer: {
    borderTop: "1px solid var(--color-border)",
    padding: "1rem 2rem",
    textAlign: "center" as const,
  },
};
