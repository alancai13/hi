"use client";

import { useState } from "react";
import { GeneratorForm } from "@/components/GeneratorForm";
import { ResultPanel } from "@/components/ResultPanel";
import { createJob, pollJob } from "@/lib/api";
import type { FormValues, JobResult } from "@/types";

type PageState =
  | { phase: "idle" }
  | { phase: "submitting" }
  | { phase: "polling"; jobId: string }
  | { phase: "done"; result: JobResult }
  | { phase: "error"; message: string };

export default function HomePage() {
  const [state, setState] = useState<PageState>({ phase: "idle" });

  const handleSubmit = async (values: FormValues) => {
    setState({ phase: "submitting" });
    try {
      const { job_id } = await createJob(values);
      setState({ phase: "polling", jobId: job_id });
      const result = await pollJob(job_id, {
        onStatusChange: () => setState({ phase: "polling", jobId: job_id }),
      });
      setState({ phase: "done", result });
    } catch (err) {
      setState({ phase: "error", message: err instanceof Error ? err.message : "Unexpected error" });
    }
  };

  const isLoading = state.phase === "submitting" || state.phase === "polling";

  return (
    <div style={s.page}>
      <div style={s.hero}>
        <h1 style={s.heading}>E2E Test Generator</h1>
        <p style={s.sub}>
          Provide a URL, acceptance criteria, and any relevant files or screenshots.
          TestGen will inspect the page and generate a Playwright test script.
        </p>
      </div>

      <GeneratorForm onSubmit={handleSubmit} isLoading={isLoading} />

      {state.phase !== "idle" && state.phase !== "submitting" && (
        <div style={s.results}>
          <ResultPanel
            phase={state.phase === "polling" ? "polling" : state.phase === "done" ? "done" : "error"}
            result={state.phase === "done" ? state.result : undefined}
            jobId={state.phase === "polling" ? state.jobId : undefined}
            errorMessage={state.phase === "error" ? state.message : undefined}
            onReset={() => setState({ phase: "idle" })}
          />
        </div>
      )}
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: {
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
  },
  hero: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  heading: {
    fontSize: "1.5rem",
    fontWeight: 700,
    letterSpacing: "-0.03em",
    color: "var(--text)",
  },
  sub: {
    fontSize: "0.875rem",
    color: "var(--text-2)",
    maxWidth: "560px",
    lineHeight: 1.65,
  },
  results: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
};
