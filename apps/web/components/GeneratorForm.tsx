"use client";

/**
 * components/GeneratorForm.tsx
 *
 * The main input form. Collects:
 *   - Target URL
 *   - Requirements / acceptance criteria (textarea)
 *   - Output format (dropdown)
 *
 * Calls onSubmit with validated FormValues.
 * Disables itself while isLoading is true.
 */

import { useState } from "react";
import type { FormValues } from "@/types";

interface Props {
  onSubmit: (values: FormValues) => void;
  isLoading: boolean;
}

export function GeneratorForm({ onSubmit, isLoading }: Props) {
  const [targetUrl, setTargetUrl] = useState("");
  const [requirements, setRequirements] = useState("");
  const [outputFormat, setOutputFormat] = useState<"playwright" | "robot">("playwright");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUrl.trim() || !requirements.trim()) return;
    onSubmit({ targetUrl: targetUrl.trim(), requirements: requirements.trim(), outputFormat });
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      {/* ── Target URL ────────────────────────────────────────────────────── */}
      <div style={styles.field}>
        <label style={styles.label} htmlFor="targetUrl">
          Target URL
        </label>
        <input
          id="targetUrl"
          type="url"
          placeholder="https://example.com/login"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          required
          disabled={isLoading}
          style={styles.input}
        />
      </div>

      {/* ── Requirements ──────────────────────────────────────────────────── */}
      <div style={styles.field}>
        <label style={styles.label} htmlFor="requirements">
          Requirements / acceptance criteria
        </label>
        <textarea
          id="requirements"
          placeholder="Describe the test scenario in plain English. E.g. 'User can log in with a valid email and password and is redirected to the dashboard.'"
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          required
          disabled={isLoading}
          rows={5}
          style={{ ...styles.input, ...styles.textarea }}
        />
        <span style={styles.hint}>Aim for 1–3 clear acceptance criteria.</span>
      </div>

      {/* ── Output format ─────────────────────────────────────────────────── */}
      <div style={styles.field}>
        <label style={styles.label} htmlFor="outputFormat">
          Output format
        </label>
        <select
          id="outputFormat"
          value={outputFormat}
          onChange={(e) => setOutputFormat(e.target.value as "playwright" | "robot")}
          disabled={isLoading}
          style={{ ...styles.input, ...styles.select }}
        >
          <option value="playwright">Playwright Test (TypeScript)</option>
          <option value="robot" disabled>
            Robot Framework (coming soon)
          </option>
        </select>
      </div>

      {/* ── Submit ────────────────────────────────────────────────────────── */}
      <button type="submit" disabled={isLoading} style={styles.button}>
        {isLoading ? "Generating…" : "Generate test script"}
      </button>
    </form>
  );
}

const styles: Record<string, React.CSSProperties> = {
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1.25rem",
    background: "var(--color-surface)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius-lg)",
    padding: "1.75rem",
    marginBottom: "2rem",
  },
  field: {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
  },
  label: {
    fontSize: "0.875rem",
    fontWeight: 600,
    color: "var(--color-text)",
  },
  hint: {
    fontSize: "0.78rem",
    color: "var(--color-text-muted)",
  },
  input: {
    background: "var(--color-surface-2)",
    border: "1px solid var(--color-border)",
    borderRadius: "var(--radius)",
    color: "var(--color-text)",
    fontSize: "0.9rem",
    padding: "0.6rem 0.85rem",
    outline: "none",
    width: "100%",
    transition: "border-color 0.15s",
  },
  textarea: {
    resize: "vertical",
    fontFamily: "var(--font-sans)",
  },
  select: {
    cursor: "pointer",
    appearance: "auto",
  },
  button: {
    alignSelf: "flex-start",
    background: "var(--color-accent)",
    border: "none",
    borderRadius: "var(--radius)",
    color: "#fff",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: 600,
    padding: "0.65rem 1.5rem",
    transition: "background 0.15s",
  },
};
