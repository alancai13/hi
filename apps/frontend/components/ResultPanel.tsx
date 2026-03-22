"use client";

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
    <div style={s.container}>
      <div style={s.header}>
        <span className="section-label">Result</span>
        <button onClick={onReset} style={s.resetBtn}>← New request</button>
      </div>

      <JobStatus
        phase={phase}
        status={result?.status}
        jobId={jobId ?? result?.job_id}
        errorMessage={errorMessage ?? result?.error_message ?? undefined}
      />

      {result?.scenario_summary && <ScenarioSummary summary={result.scenario_summary} />}
      {result?.warnings && result.warnings.length > 0 && <WarningsPanel warnings={result.warnings} />}
      {(phase === "done" || result?.generated_code) && (
        <CodePreview code={result?.generated_code ?? null} outputFormat={result?.output_format} />
      )}
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  resetBtn: {
    background: "none",
    border: "1px solid var(--border-2)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-3)",
    cursor: "pointer",
    fontSize: "0.75rem",
    padding: "0.3rem 0.7rem",
    fontFamily: "var(--font-sans)",
  },
};
