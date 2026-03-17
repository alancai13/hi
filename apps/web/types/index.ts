/**
 * types/index.ts — Frontend-local TypeScript types
 */

export type {
  GenerationRequest,
  GenerationWarning,
  JobResult,
  JobStatus,
  OutputFormat,
  CreateJobResponse,
  HealthResponse,
} from "../../../packages/shared/types";

/** Values collected by the GeneratorForm. */
export interface FormValues {
  targetUrl: string;
  requirements: string;
  outputFormat: "playwright" | "robot";
  /** Uploaded requirement documents (.pdf, .docx, .md, .txt) */
  requirementFiles: File[];
  /** Uploaded screenshots (.png, .jpg, .webp, etc.) */
  screenshots: File[];
}

export type ResultPhase = "polling" | "done" | "error";
