"use client";

/**
 * app/page.tsx — Main page
 *
 * Renders the generation form and the result panel.
 * Manages top-level state: job ID, poll status, final result.
 *
 * TODO: Extract state management into a custom hook (useGenerationJob)
 *       once the API client is wired to a real backend.
 */

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

      // TODO: Replace with SSE or WebSocket subscription when available.
      //       Currently polls every 1.5 seconds until completed or failed.
      const result = await pollJob(job_id, {
        onStatusChange: (status) => {
          // Re-render with updated phase while still polling
          setState({ phase: "polling", jobId: job_id });
          console.info("Job status:", status);
        },
      });

      setState({ phase: "done", result });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected error";
      setState({ phase: "error", message });
    }
  };

  const handleReset = () => setState({ phase: "idle" });

  return (
    <div>
      <section style={styles.hero}>
        <h1 style={styles.heading}>Generate E2E Test Scripts</h1>
        <p style={styles.subheading}>
          Enter a URL and your acceptance criteria — TestGen will inspect the page and
          generate a Playwright test script.
        </p>
      </section>

      <GeneratorForm
        onSubmit={handleSubmit}
        isLoading={state.phase === "submitting" || state.phase === "polling"}
      />

      {(state.phase === "polling" ||
        state.phase === "done" ||
        state.phase === "error") && (
        <ResultPanel
          phase={state.phase}
          result={state.phase === "done" ? state.result : undefined}
          jobId={state.phase === "polling" ? state.jobId : undefined}
          errorMessage={state.phase === "error" ? state.message : undefined}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  hero: {
    marginBottom: "2rem",
  },
  heading: {
    fontSize: "1.75rem",
    fontWeight: 700,
    letterSpacing: "-0.03em",
    marginBottom: "0.5rem",
  },
  subheading: {
    color: "var(--color-text-muted)",
    maxWidth: "600px",
    lineHeight: 1.6,
  },
};
