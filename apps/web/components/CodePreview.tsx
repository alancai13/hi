"use client";

import { useState } from "react";
import type { OutputFormat } from "@/types";

interface Props {
  code: string | null;
  outputFormat?: OutputFormat;
}

const EXT: Record<string, string> = {
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
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `testgen_script${EXT[outputFormat] ?? ".txt"}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={s.card}>
      <div style={s.toolbar}>
        <span className="section-label">Generated script</span>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          <button onClick={handleCopy} disabled={!code} style={s.btn}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <button onClick={handleDownload} disabled={!code} style={s.btn}>
            Download{EXT[outputFormat] ?? ""}
          </button>
        </div>
      </div>

      {code ? (
        <pre style={s.pre}><code>{code}</code></pre>
      ) : (
        <div style={s.empty}>
          <span style={{ color: "var(--text-3)", fontSize: "0.82rem" }}>
            Script will appear here once generation completes.
          </span>
        </div>
      )}
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    overflow: "hidden",
  },
  toolbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0.7rem 1.1rem",
    borderBottom: "1px solid var(--border)",
    background: "var(--surface-2)",
  },
  btn: {
    background: "var(--surface-3)",
    border: "1px solid var(--border-2)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-2)",
    cursor: "pointer",
    fontSize: "0.75rem",
    padding: "0.25rem 0.65rem",
    fontFamily: "var(--font-sans)",
  },
  pre: {
    overflowX: "auto",
    padding: "1.1rem 1.25rem",
    fontSize: "0.8rem",
    lineHeight: 1.7,
    color: "var(--text)",
    background: "var(--surface)",
    margin: 0,
    whiteSpace: "pre",
  },
  empty: {
    padding: "2rem",
    textAlign: "center" as const,
    background: "var(--surface)",
  },
};
