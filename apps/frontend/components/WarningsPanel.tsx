"use client";

import type { GenerationWarning } from "@/types";

interface Props {
  warnings: GenerationWarning[];
}

const SEV_COLOR: Record<string, string> = {
  info: "var(--info)",
  warning: "var(--warning)",
  error: "var(--error)",
};

const SEV_ICON: Record<string, string> = {
  info: "ℹ",
  warning: "⚠",
  error: "✕",
};

export function WarningsPanel({ warnings }: Props) {
  if (warnings.length === 0) return null;

  return (
    <div style={s.card}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.65rem" }}>
        <span className="section-label">Warnings</span>
        <span style={s.count}>{warnings.length}</span>
      </div>
      <ul style={s.list}>
        {warnings.map((w, i) => (
          <li key={i} style={s.item}>
            <span style={{ color: SEV_COLOR[w.severity] ?? "var(--text-2)", flexShrink: 0, fontSize: "0.8rem" }}>
              {SEV_ICON[w.severity] ?? "•"}
            </span>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.15rem" }}>
              <span style={{ fontSize: "0.82rem" }}>{w.message}</span>
              {w.element && (
                <code style={{ fontSize: "0.73rem", color: "var(--text-3)" }}>{w.element}</code>
              )}
            </div>
            <span style={{ ...s.sevBadge, color: SEV_COLOR[w.severity] ?? "var(--text-2)" }}>
              {w.severity}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "0.9rem 1.1rem",
  },
  count: {
    fontSize: "0.7rem",
    background: "var(--surface-3)",
    borderRadius: "999px",
    padding: "0.05rem 0.45rem",
    color: "var(--text-2)",
  },
  list: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
  },
  item: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.55rem",
    padding: "0.5rem 0.65rem",
    background: "var(--surface-2)",
    borderRadius: "var(--radius-sm)",
  },
  sevBadge: {
    fontSize: "0.68rem",
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "0.04em",
    flexShrink: 0,
  },
};
