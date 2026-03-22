/**
 * packages/shared/types/index.ts
 *
 * Shared TypeScript types mirroring the backend Pydantic schemas.
 * These are the source of truth for the API contract on the frontend side.
 *
 * Keep in sync with: apps/backend/app/schemas/generation.py
 */

// ─── Enums ────────────────────────────────────────────────────────────────────

export type OutputFormat = "playwright" | "robot";

export type JobStatus = "pending" | "running" | "completed" | "failed";

export type WarningSeverity = "info" | "warning" | "error";

export type WarningType =
  | "selector_fragile"
  | "requirement_ambiguous"
  | "element_not_found"
  | "page_unreachable";

// ─── Request ──────────────────────────────────────────────────────────────────

export interface GenerationRequest {
  /** The URL of the web application to test. Must be a valid http/https URL. */
  target_url: string;

  /** Plain-English acceptance criteria or test scenario description. */
  requirements: string;

  /** The output format for the generated test script. Defaults to "playwright". */
  output_format?: OutputFormat;
}

// ─── Response shapes ──────────────────────────────────────────────────────────

export interface GenerationWarning {
  type: WarningType;
  severity: WarningSeverity;
  message: string;
  /** The selector or element reference that triggered this warning (if applicable). */
  element?: string;
}

export interface CreateJobResponse {
  job_id: string;
  status: "pending";
  created_at: string; // ISO 8601
}

export interface JobResult {
  job_id: string;
  status: JobStatus;
  created_at: string; // ISO 8601
  completed_at: string | null;

  /** Human-readable summary of the inferred test scenario. */
  scenario_summary: string | null;

  /** Warnings about selector fragility, ambiguous requirements, etc. */
  warnings: GenerationWarning[];

  /** The generated test script code. */
  generated_code: string | null;

  output_format: OutputFormat;

  /** Present when status === "failed". */
  error_message: string | null;
}

// ─── Health check ─────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: "ok";
  version: string;
}
