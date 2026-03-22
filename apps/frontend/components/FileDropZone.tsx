"use client";

/**
 * components/FileDropZone.tsx
 *
 * Reusable drag-and-drop file upload zone.
 * Supports click-to-browse, drag-and-drop, multi-file, image previews,
 * and per-file removal.
 */

import { useCallback, useRef, useState } from "react";

interface Props {
  /** Accepted MIME type string for the hidden <input> (e.g. ".pdf,.docx,.md,.txt") */
  accept: string;
  /** Label shown inside the drop zone */
  label: string;
  /** Sub-label (accepted extensions hint) */
  hint: string;
  files: File[];
  onChange: (files: File[]) => void;
  /** If true, show image thumbnail previews instead of file icons */
  showPreviews?: boolean;
  /** Max number of files (0 = unlimited) */
  maxFiles?: number;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  );
}

function ImageIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <circle cx="8.5" cy="8.5" r="1.5"/>
      <polyline points="21 15 16 10 5 21"/>
    </svg>
  );
}

export function FileDropZone({
  accept,
  label,
  hint,
  files,
  onChange,
  showPreviews = false,
  maxFiles = 0,
}: Props) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const addFiles = useCallback(
    (incoming: FileList | null) => {
      if (!incoming) return;
      const next = [...files];
      for (const f of Array.from(incoming)) {
        if (!next.find((x) => x.name === f.name && x.size === f.size)) {
          next.push(f);
        }
      }
      onChange(maxFiles > 0 ? next.slice(0, maxFiles) : next);
    },
    [files, onChange, maxFiles]
  );

  const remove = (index: number) => {
    const next = files.filter((_, i) => i !== index);
    onChange(next);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };
  const onDragLeave = () => setDragging(false);
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const empty = files.length === 0;

  return (
    <div style={s.wrapper}>
      {/* Drop zone / click target */}
      <div
        role="button"
        tabIndex={0}
        aria-label={`${label} — click or drop files`}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        style={{
          ...s.zone,
          borderColor: dragging ? "var(--border-focus)" : "var(--border-2)",
          background: dragging ? "var(--surface-3)" : "var(--surface-2)",
        }}
      >
        <div style={{ color: "var(--text-3)" }}>
          {showPreviews ? <ImageIcon /> : <UploadIcon />}
        </div>
        <div style={s.zoneText}>
          <span style={s.zoneLabel}>{label}</span>
          <span style={s.zoneHint}>{hint}</span>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={maxFiles !== 1}
        style={{ display: "none" }}
        onChange={(e) => addFiles(e.target.files)}
        // Reset value so the same file can be re-added after removal
        onClick={(e) => ((e.target as HTMLInputElement).value = "")}
      />

      {/* File list */}
      {!empty && (
        <ul style={s.list}>
          {files.map((file, i) => (
            <li key={`${file.name}-${i}`} style={s.item}>
              {showPreviews ? (
                <ImageThumb file={file} />
              ) : (
                <span style={{ color: "var(--text-3)", flexShrink: 0 }}>
                  <FileIcon />
                </span>
              )}
              <span style={s.fileName} title={file.name}>
                {file.name}
              </span>
              <span style={s.fileSize}>{formatBytes(file.size)}</span>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); remove(i); }}
                style={s.removeBtn}
                aria-label={`Remove ${file.name}`}
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** Shows a small thumbnail for image files. */
function ImageThumb({ file }: { file: File }) {
  const src = URL.createObjectURL(file);
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={file.name}
      style={{ width: 32, height: 32, objectFit: "cover", borderRadius: "var(--radius-sm)", flexShrink: 0 }}
      onLoad={() => URL.revokeObjectURL(src)}
    />
  );
}

const s: Record<string, React.CSSProperties> = {
  wrapper: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  zone: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "0.6rem",
    padding: "1.5rem 1rem",
    border: "1px dashed",
    borderRadius: "var(--radius)",
    cursor: "pointer",
    userSelect: "none",
    transition: "border-color 0.15s, background 0.15s",
    textAlign: "center",
  },
  zoneText: {
    display: "flex",
    flexDirection: "column",
    gap: "0.2rem",
  },
  zoneLabel: {
    fontSize: "0.82rem",
    fontWeight: 500,
    color: "var(--text-2)",
  },
  zoneHint: {
    fontSize: "0.72rem",
    color: "var(--text-3)",
  },
  list: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: "0.35rem",
  },
  item: {
    display: "flex",
    alignItems: "center",
    gap: "0.55rem",
    padding: "0.45rem 0.65rem",
    background: "var(--surface-3)",
    borderRadius: "var(--radius-sm)",
    fontSize: "0.8rem",
  },
  fileName: {
    flex: 1,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    color: "var(--text)",
  },
  fileSize: {
    flexShrink: 0,
    color: "var(--text-3)",
    fontSize: "0.72rem",
  },
  removeBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "var(--text-3)",
    fontSize: "0.75rem",
    padding: "0 0.15rem",
    lineHeight: 1,
    flexShrink: 0,
    transition: "color 0.1s",
  },
};
