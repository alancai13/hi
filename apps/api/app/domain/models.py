"""
app/domain/models.py — Core domain models

Internal representations used by the generation pipeline.
Richer than the HTTP schemas in app/schemas/.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


# ─── Enums ────────────────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class OutputFormat(str, Enum):
    playwright = "playwright"
    robot = "robot"


# ─── Uploaded file ────────────────────────────────────────────────────────────

@dataclass
class UploadedFile:
    """A file the user attached to the generation request."""
    filename: str
    content_type: str
    data: bytes

    @property
    def is_image(self) -> bool:
        return self.content_type.startswith("image/")

    @property
    def text_content(self) -> str | None:
        """Decode file to text if it's a text-based format."""
        text_types = {"text/plain", "text/markdown", "text/x-markdown"}
        text_extensions = {".txt", ".md", ".rst"}
        ext = "." + self.filename.rsplit(".", 1)[-1].lower() if "." in self.filename else ""
        if self.content_type in text_types or ext in text_extensions:
            try:
                return self.data.decode("utf-8", errors="replace")
            except Exception:
                return None
        return None  # PDF/DOCX require dedicated extraction (future)


# ─── Page inspection ──────────────────────────────────────────────────────────

@dataclass
class PageElement:
    """A single interactive element found on the target page."""
    tag: str                        # input, button, a, select, textarea
    element_type: str | None        # input type attr (text, email, password…)
    text: str | None                # visible text / button label
    name: str | None                # name attribute
    element_id: str | None          # id attribute
    placeholder: str | None
    aria_label: str | None
    data_testid: str | None
    href: str | None = None         # for <a> tags
    required: bool = False


@dataclass
class PageSnapshot:
    """Everything Playwright captured about the target URL."""
    url: str
    title: str
    meta_description: str | None = None
    screenshot_bytes: bytes | None = None   # PNG bytes of viewport
    headings: list[dict] = field(default_factory=list)       # [{level, text}]
    elements: list[PageElement] = field(default_factory=list)
    page_text_excerpt: str | None = None    # visible text, first 2000 chars


# ─── Generation output ────────────────────────────────────────────────────────

@dataclass
class GenerationWarning:
    """A quality signal emitted during any pipeline stage."""
    type: str       # selector_fragile | requirement_ambiguous | page_unreachable …
    severity: str   # info | warning | error
    message: str
    element: str | None = None


@dataclass
class GeneratedArtifact:
    """The final output of the generation pipeline."""
    job_id: str
    output_format: OutputFormat
    code: str
    scenario_summary: str
    warnings: list[GenerationWarning] = field(default_factory=list)
    model_used: str | None = None


# ─── Job ──────────────────────────────────────────────────────────────────────

@dataclass
class TestScenarioInput:
    """Normalised user intent from the HTTP request."""
    target_url: str
    requirements: str
    output_format: OutputFormat = OutputFormat.playwright


@dataclass
class GenerationJob:
    """Full lifecycle of a single generation request."""
    job_id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.pending
    input: TestScenarioInput | None = None
    requirement_files: list[UploadedFile] = field(default_factory=list)
    screenshots: list[UploadedFile] = field(default_factory=list)
    artifact: GeneratedArtifact | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
