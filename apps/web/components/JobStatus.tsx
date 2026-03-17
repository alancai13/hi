"use client";

/**
 * components/JobStatus.tsx
 *
 * Displays the current job status as a badge + descriptive text.
 * Shows a spinner while polling, success/error states when done.
 */

interface Props {
  phase: "polling" | "done" | "error";
  status?: string;
  jobId?: string;
  errorMessage?: string;
}

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  running: "Running…",
  completed: "Completed",
  failed: "Failed",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "var(--color-text-muted)",
  running: "var(--color-accent)",
  completed: "var(--color-success)",
  failed: "var(--color-error)",
};

export function JobStatus({ phase, status, jobId, errorMessage }: Props) {
  const displayStatus = status ?? (phase === "polling" ? "pending" : phase === "error" ? "failed" : "completed");
  const color = STATUS_COLORS[displayStatus] ?? "var(--color-text-muted)";

  return (
    <div style={styles.card}>
      <div style={styles.row}>
        <span style={styles.label}>Status</span>
        <span style={{ ...styles.badge, color, borderColor: color }}>
          {phase === "polling" && "⟳ "}
          {STATUS_LABELS[displayStatus] ?? displayStatus}
        </span>
      </div>

      {jobId && (
        <div style={styles.row}>
          <span style={styles.label}>Job ID</span>
          <code style={styles.code}>{jobId}</code>
        </div>
      )}

      {errorMessage && (
        <div style={{ ...styles.row, marginTop: "0.5rem" }}>
          <span style={{ ...styles.label, color: "var(--color-error)" }}>Error</span>
          <span style={{ color: "var(--color-error)", fontSize: "0.875rem" }}>{errorMessage}</span>
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
    padding: "1rem 1.25rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
  },
  label: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "var(--color-text-muted)",
    minWidth: "70px",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
  },
  badge: {
    fontSize: "0.85rem",
    fontWeight: 600,
    border: "1px solid",
    borderRadius: "999px",
    padding: "0.15rem 0.65rem",
  },
  code: {
    fontFamily: "var(--font-mono)",
    fontSize: "0.8rem",
    color: "var(--color-text-muted)",
  },
};
