"use client";

interface Props {
  summary: string | null;
}

export function ScenarioSummary({ summary }: Props) {
  return (
    <div style={s.card}>
      <span className="section-label" style={{ marginBottom: "0.5rem", display: "block" }}>
        Scenario summary
      </span>
      {summary ? (
        <p style={{ fontSize: "0.875rem", lineHeight: 1.65, color: "var(--text)" }}>{summary}</p>
      ) : (
        <div style={s.skeleton} />
      )}
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
  skeleton: {
    height: "0.85rem",
    borderRadius: "var(--radius-sm)",
    background: "var(--surface-3)",
    width: "75%",
  },
};
