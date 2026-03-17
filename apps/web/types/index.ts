/**
 * types/index.ts — Frontend-local TypeScript types
 *
 * These re-export and extend the shared types from packages/shared.
 * Import from here (not directly from packages/shared) in components.
 */

// Re-export shared API types
export type {
  GenerationRequest,
  GenerationWarning,
  JobResult,
  JobStatus,
  OutputFormat,
  CreateJobResponse,
  HealthResponse,
} from "../../../packages/shared/types";

// ─── Frontend-specific types ──────────────────────────────────────────────────

/** Values collected by the GeneratorForm component. */
export interface FormValues {
  targetUrl: string;
  requirements: string;
  outputFormat: "playwright" | "robot";
}

/** Props passed between page and result panel. */
export type ResultPhase = "polling" | "done" | "error";
