"use client";

/**
 * components/ScenarioSummary.tsx
 *
 * Displays the human-readable summary of the inferred test scenario.
 * Shows a placeholder skeleton while loading.
 */

interface Props {
  summary: string | null;
}

export function ScenarioSummary({ summary }: Props) {
  return (
    <div style={styles.card}>
      <h3 style={styles.heading}>Scenario summary</h3>
      {summary ? (
        <p style={styles.text}>{summary}</p>
      ) : (
        <div style={styles.skeleton} aria-busy="true" aria-label="Loading scenario summary" />
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
  },
  heading: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "var(--color-text-muted)",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    marginBottom: "0.6rem",
  },
  text: {
    fontSize: "0.925rem",
    lineHeight: 1.6,
  },
  skeleton: {
    height: "1rem",
    borderRadius: "4px",
    background: "var(--color-surface-2)",
    width: "80%",
    animation: "pulse 1.5s ease-in-out infinite",
  },
};
