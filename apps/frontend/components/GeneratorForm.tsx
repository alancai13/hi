"use client";

/**
 * components/GeneratorForm.tsx
 *
 * Main input form. Sections:
 *   1. Target URL
 *   2. Requirements & context (textarea)
 *   3. Uploads — requirement files + screenshots (two columns)
 *   4. Output format + submit
 */

import { useState } from "react";
import { FileDropZone } from "./FileDropZone";
import type { FormValues } from "@/types";

interface Props {
  onSubmit: (values: FormValues) => void;
  isLoading: boolean;
}

export function GeneratorForm({ onSubmit, isLoading }: Props) {
  const [targetUrl, setTargetUrl] = useState("");
  const [requirements, setRequirements] = useState("");
  const [outputFormat, setOutputFormat] = useState<"playwright" | "robot">("playwright");
  const [requirementFiles, setRequirementFiles] = useState<File[]>([]);
  const [screenshots, setScreenshots] = useState<File[]>([]);

  const canSubmit = targetUrl.trim().length > 0 || requirements.trim().length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || isLoading) return;
    onSubmit({
      targetUrl: targetUrl.trim(),
      requirements: requirements.trim(),
      outputFormat,
      requirementFiles,
      screenshots,
    });
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div style={s.stack}>

        {/* ── 1. Target URL ───────────────────────────────────────────── */}
        <div style={s.section}>
          <label className="section-label" htmlFor="targetUrl">
            Target URL
          </label>
          <div style={s.urlRow}>
            <input
              id="targetUrl"
              type="url"
              className="field-input"
              placeholder="https://example.com/login"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              disabled={isLoading}
              autoComplete="off"
              spellCheck={false}
            />
          </div>
          <p style={s.hint}>The page you want to generate a test for.</p>
        </div>

        <Divider />

        {/* ── 2. Requirements & context ───────────────────────────────── */}
        <div style={s.section}>
          <label className="section-label" htmlFor="requirements">
            Requirements &amp; Context
          </label>
          <textarea
            id="requirements"
            className="field-input"
            placeholder={REQUIREMENTS_PLACEHOLDER}
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            disabled={isLoading}
            rows={7}
            style={{ resize: "vertical", fontFamily: "var(--font-sans)", lineHeight: 1.65 }}
          />
          <p style={s.hint}>
            Plain-English acceptance criteria, user stories, or any context that describes
            what the test should verify.
          </p>
        </div>

        <Divider />

        {/* ── 3. Uploads ──────────────────────────────────────────────── */}
        <div style={s.section}>
          <span className="section-label">Attachments</span>
          <p style={{ ...s.hint, marginBottom: "0.85rem" }}>
            Optionally attach requirement documents or screenshots to give the generator more
            context. These are passed to the pipeline alongside your written requirements.
          </p>

          <div style={s.uploadGrid}>
            {/* Requirement files */}
            <div style={s.uploadCol}>
              <span style={s.colLabel}>Requirement files</span>
              <FileDropZone
                accept=".pdf,.docx,.doc,.md,.txt,.rtf"
                label="Drop files or click to browse"
                hint=".pdf · .docx · .md · .txt"
                files={requirementFiles}
                onChange={setRequirementFiles}
                showPreviews={false}
              />
            </div>

            {/* Screenshots */}
            <div style={s.uploadCol}>
              <span style={s.colLabel}>Screenshots</span>
              <FileDropZone
                accept="image/png,image/jpeg,image/webp,image/gif"
                label="Drop images or click to browse"
                hint=".png · .jpg · .webp"
                files={screenshots}
                onChange={setScreenshots}
                showPreviews={true}
              />
            </div>
          </div>
        </div>

        <Divider />

        {/* ── 4. Output format + submit ───────────────────────────────── */}
        <div style={s.footer}>
          <div style={s.formatField}>
            <label className="section-label" htmlFor="outputFormat" style={{ display: "block", marginBottom: "0.4rem" }}>
              Output format
            </label>
            <select
              id="outputFormat"
              className="field-input"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value as "playwright" | "robot")}
              disabled={isLoading}
              style={{ width: "auto", minWidth: "210px", cursor: "pointer" }}
            >
              <option value="playwright">Playwright Test (TypeScript)</option>
              <option value="robot" disabled>Robot Framework — coming soon</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={!canSubmit || isLoading}
            style={{
              ...s.submitBtn,
              opacity: !canSubmit || isLoading ? 0.4 : 1,
              cursor: !canSubmit || isLoading ? "not-allowed" : "pointer",
            }}
          >
            {isLoading ? (
              <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Spinner /> Generating…
              </span>
            ) : (
              "Generate script →"
            )}
          </button>
        </div>

      </div>
    </form>
  );
}

function Divider() {
  return <div style={{ height: "1px", background: "var(--border)" }} />;
}

function Spinner() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      style={{ animation: "spin 0.8s linear infinite" }}
    >
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );
}

const REQUIREMENTS_PLACEHOLDER = `Example:
- User can log in with a valid email and password
- After submitting, they should be redirected to /dashboard
- An error message should appear if the password is wrong

Describe what the test should verify in plain English.`;

const s: Record<string, React.CSSProperties> = {
  stack: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
  },
  section: {
    padding: "1.5rem 1.75rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.55rem",
  },
  urlRow: {
    display: "flex",
    gap: "0.5rem",
  },
  hint: {
    fontSize: "0.75rem",
    color: "var(--text-3)",
    lineHeight: 1.5,
  },
  uploadGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "1.25rem",
  },
  uploadCol: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  colLabel: {
    fontSize: "0.78rem",
    fontWeight: 500,
    color: "var(--text-2)",
  },
  footer: {
    padding: "1.25rem 1.75rem",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: "1rem",
    flexWrap: "wrap" as const,
    background: "var(--surface-2)",
  },
  formatField: {
    display: "flex",
    flexDirection: "column",
  },
  submitBtn: {
    background: "var(--text)",
    color: "var(--bg)",
    border: "none",
    borderRadius: "var(--radius)",
    fontFamily: "var(--font-sans)",
    fontSize: "0.875rem",
    fontWeight: 600,
    padding: "0.65rem 1.4rem",
    transition: "opacity 0.15s",
    whiteSpace: "nowrap" as const,
  },
};
