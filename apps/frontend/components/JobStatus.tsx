"use client";

interface Props {
  phase: "polling" | "done" | "error";
  status?: string;
  jobId?: string;
  errorMessage?: string;
}

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "var(--text-2)",
  running: "var(--text)",
  completed: "var(--success)",
  failed: "var(--error)",
};

export function JobStatus({ phase, status, jobId, errorMessage }: Props) {
  const displayStatus = status ?? (phase === "error" ? "failed" : phase === "done" ? "completed" : "pending");
  const color = STATUS_COLORS[displayStatus] ?? "var(--text-2)";
  const isPending = phase === "polling";

  return (
    <div style={s.card}>
      <div style={s.row}>
        <span style={s.key}>Status</span>
        <span style={{ ...s.badge, color, borderColor: color }}>
          {isPending && <PulsingDot />}
          {STATUS_LABELS[displayStatus] ?? displayStatus}
        </span>
      </div>

      {jobId && (
        <div style={s.row}>
          <span style={s.key}>Job ID</span>
          <code style={s.code}>{jobId}</code>
        </div>
      )}

      {errorMessage && (
        <div style={{ ...s.row, marginTop: "0.4rem" }}>
          <span style={{ ...s.key, color: "var(--error)" }}>Error</span>
          <span style={{ color: "var(--error)", fontSize: "0.82rem" }}>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

function PulsingDot() {
  return (
    <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%",
      background: "currentColor", marginRight: "0.4rem", verticalAlign: "middle",
      animation: "pulse-dot 1.2s ease-in-out infinite" }}>
      <style>{`@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }`}</style>
    </span>
  );
}

const s: Record<string, React.CSSProperties> = {
  card: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding: "0.9rem 1.1rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.45rem",
  },
  row: { display: "flex", alignItems: "center", gap: "0.75rem" },
  key: {
    fontSize: "0.72rem",
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "0.07em",
    color: "var(--text-3)",
    minWidth: "60px",
  },
  badge: {
    fontSize: "0.8rem",
    fontWeight: 600,
    border: "1px solid",
    borderRadius: "999px",
    padding: "0.1rem 0.6rem",
    display: "inline-flex",
    alignItems: "center",
  },
  code: {
    fontFamily: "var(--font-mono)",
    fontSize: "0.75rem",
    color: "var(--text-2)",
  },
};
