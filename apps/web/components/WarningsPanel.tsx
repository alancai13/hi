"use client";

/**
 * components/WarningsPanel.tsx
 *
 * Displays a list of GenerationWarnings from the backend.
 * Each warning shows its severity badge, message, and optionally the element selector.
 */

import type { GenerationWarning } from "@/types";

interface Props {
  warnings: GenerationWarning[];
}

const SEVERITY_COLORS: Record<string, string> = {
  info: "var(--color-text-muted)",
  warning: "var(--color-warning)",
  error: "var(--color-error)",
};

const SEVERITY_ICONS: Record<string, string> = {
  info: "ℹ",
  warning: "⚠",
  error: "✕",
};

export function WarningsPanel({ warnings }: Props) {
  if (warnings.length === 0) return null;

  return (
    <div style={styles.card}>
      <h3 style={styles.heading}>
        Warnings &amp; selector confidence
        <span style={styles.count}>{warnings.length}</span>
      </h3>
      <ul style={styles.list}>
        {warnings.map((w, i) => (
          <li key={i} style={styles.item}>
            <span
              style={{
                ...styles.icon,
                color: SEVERITY_COLORS[w.severity] ?? "var(--color-text-muted)",
              }}
            >
              {SEVERITY_ICONS[w.severity] ?? "•"}
            </span>
            <div style={styles.content}>
              <span style={styles.message}>{w.message}</span>
              {w.element && (
                <code style={styles.selector}>{w.element}</code>
              )}
            </div>
            <span
              style={{
                ...styles.badge,
                color: SEVERITY_COLORS[w.severity] ?? "var(--color-text-muted)",
              }}
            >
              {w.severity}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius)",
    padding: "1rem 1.25rem",
  },
  heading: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "var(--color-text-muted)",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    marginBottom: "0.75rem",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
  },
  count: {
    background: "var(--color-surface-2)",
    borderRadius: "999px",
    fontSize: "0.75rem",
    padding: "0.1rem 0.5rem",
    color: "var(--color-text)",
  },
  list: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: "0.6rem",
  },
  item: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.6rem",
    padding: "0.6rem 0.75rem",
    background: "var(--color-surface-2)",
    borderRadius: "var(--radius)",
  },
  icon: {
    fontSize: "0.9rem",
    flexShrink: 0,
    marginTop: "1px",
  },
  content: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "0.2rem",
  },
  message: {
    fontSize: "0.875rem",
  },
  selector: {
    fontSize: "0.78rem",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-mono)",
  },
  badge: {
    fontSize: "0.72rem",
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "0.04em",
    flexShrink: 0,
  },
};
