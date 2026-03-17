"use client";

/**
 * components/ResultPanel.tsx
 *
 * Container for all result sections. Rendered once the job is submitted.
 * Delegates display to child components for each result section.
 */

import { JobStatus } from "./JobStatus";
import { ScenarioSummary } from "./ScenarioSummary";
import { WarningsPanel } from "./WarningsPanel";
import { CodePreview } from "./CodePreview";
import type { JobResult } from "@/types";

interface Props {
  phase: "polling" | "done" | "error";
  result?: JobResult;
  jobId?: string;
  errorMessage?: string;
  onReset: () => void;
}

export function ResultPanel({ phase, result, jobId, errorMessage, onReset }: Props) {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.heading}>Result</h2>
        <button onClick={onReset} style={styles.resetButton}>
          ← New request
        </button>
      </div>

      {/* ── Job status ───────────────────────────────────────────────────── */}
      <JobStatus
        phase={phase}
        status={result?.status}
        jobId={jobId ?? result?.job_id}
        errorMessage={errorMessage ?? result?.error_message ?? undefined}
      />

      {/* ── Scenario summary ─────────────────────────────────────────────── */}
      {(phase === "done" || result?.scenario_summary) && (
        <ScenarioSummary summary={result?.scenario_summary ?? null} />
      )}

      {/* ── Warnings ─────────────────────────────────────────────────────── */}
      {result?.warnings && result.warnings.length > 0 && (
        <WarningsPanel warnings={result.warnings} />
      )}

      {/* ── Generated code preview ───────────────────────────────────────── */}
      {(phase === "done" || result?.generated_code) && (
        <CodePreview code={result?.generated_code ?? null} outputFormat={result?.output_format} />
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "1.25rem",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  heading: {
    fontSize: "1.2rem",
    fontWeight: 700,
  },
  resetButton: {
    background: "none",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius)",
    color: "var(--color-text-muted)",
    cursor: "pointer",
    fontSize: "0.85rem",
    padding: "0.4rem 0.85rem",
  },
};
