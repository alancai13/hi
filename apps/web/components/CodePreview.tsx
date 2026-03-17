"use client";

/**
 * components/CodePreview.tsx
 *
 * Displays the generated test script with:
 *   - A plain <pre> code block (no syntax highlighter dependency yet)
 *   - Copy to clipboard button
 *   - Download as file button
 *
 * TODO: Add syntax highlighting (e.g. Shiki, Prism) when styling is polished.
 * TODO: Wire download to a real file endpoint from the backend when available.
 */

import { useState } from "react";
import type { OutputFormat } from "@/types";

interface Props {
  code: string | null;
  outputFormat?: OutputFormat;
}

const FILE_EXTENSIONS: Record<string, string> = {
  playwright: ".spec.ts",
  robot: ".robot",
};

export function CodePreview({ code, outputFormat = "playwright" }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!code) return;
    const ext = FILE_EXTENSIONS[outputFormat] ?? ".txt";
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `testgen_script${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.card}>
      <div style={styles.toolbar}>
        <h3 style={styles.heading}>Generated script</h3>
        <div style={styles.actions}>
          <button
            onClick={handleCopy}
            disabled={!code}
            style={styles.actionButton}
            title="Copy to clipboard"
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <button
            onClick={handleDownload}
            disabled={!code}
            style={styles.actionButton}
            title={`Download as ${FILE_EXTENSIONS[outputFormat] ?? ".txt"}`}
          >
            Download
          </button>
        </div>
      </div>

      {code ? (
        <pre style={styles.pre}>
          <code>{code}</code>
        </pre>
      ) : (
        <div style={styles.empty}>
          <span style={{ color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
            Script will appear here once generation is complete.
          </span>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius)",
    overflow: "hidden",
  },
  toolbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0.75rem 1.25rem",
    borderBottom: "1px solid var(--color-border)",
  },
  heading: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "var(--color-text-muted)",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
  },
  actions: {
    display: "flex",
    gap: "0.5rem",
  },
  actionButton: {
    background: "var(--color-surface-2)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius)",
    color: "var(--color-text)",
    cursor: "pointer",
    fontSize: "0.8rem",
    padding: "0.3rem 0.75rem",
  },
  pre: {
    overflowX: "auto",
    padding: "1.25rem",
    fontSize: "0.82rem",
    lineHeight: 1.65,
    color: "var(--color-text)",
    background: "var(--color-surface-2)",
    margin: 0,
    whiteSpace: "pre",
  },
  empty: {
    padding: "2rem",
    textAlign: "center" as const,
  },
};
