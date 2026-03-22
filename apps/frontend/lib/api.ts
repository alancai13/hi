/**
 * lib/api.ts — Typed API client
 *
 * All fetch calls go here. Components never call fetch() directly.
 * createJob now sends multipart/form-data to support file uploads.
 */

import type { CreateJobResponse, FormValues, JobResult } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

/**
 * POST /api/v1/generate  (multipart/form-data)
 *
 * Sends all form fields including uploaded files.
 * Note: do NOT set Content-Type header — the browser sets it with the boundary.
 */
export async function createJob(values: FormValues): Promise<CreateJobResponse> {
  const form = new FormData();
  form.append("target_url", values.targetUrl);
  form.append("requirements", values.requirements);
  form.append("output_format", values.outputFormat);

  for (const file of values.requirementFiles) {
    form.append("requirement_files", file, file.name);
  }
  for (const file of values.screenshots) {
    form.append("screenshots", file, file.name);
  }

  return request<CreateJobResponse>("/api/v1/generate", {
    method: "POST",
    body: form,
    // No Content-Type header — browser sets multipart/form-data with boundary automatically
  });
}

export async function getJob(jobId: string): Promise<JobResult> {
  return request<JobResult>(`/api/v1/jobs/${jobId}`, {
    headers: { "Content-Type": "application/json" },
  });
}

export async function pollJob(
  jobId: string,
  options: {
    intervalMs?: number;
    maxAttempts?: number;
    onStatusChange?: (status: JobResult["status"]) => void;
  } = {}
): Promise<JobResult> {
  const { intervalMs = 2000, maxAttempts = 60, onStatusChange } = options;
  let lastStatus: string | undefined;

  for (let i = 0; i < maxAttempts; i++) {
    const job = await getJob(jobId);

    if (job.status !== lastStatus) {
      lastStatus = job.status;
      onStatusChange?.(job.status);
    }

    if (job.status === "completed" || job.status === "failed") return job;

    await new Promise((r) => setTimeout(r, intervalMs));
  }

  throw new Error(`Job ${jobId} did not complete within the polling window.`);
}

export async function checkHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health", {
    headers: { "Content-Type": "application/json" },
  });
}
