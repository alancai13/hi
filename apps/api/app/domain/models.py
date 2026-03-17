"""
app/domain/models.py — Core domain models

These are the internal representations used by the generation pipeline.
They are richer and more complex than the HTTP schemas in app/schemas/.

Relationships:
  GenerationJob        → orchestrates the full lifecycle
  TestScenarioInput    → validated user intent (URL + requirements)
  PageSnapshot         → what Playwright finds on the page
  SelectorCandidate    → a proposed UI element + how stable the selector is
  TestPlan             → ordered steps and assertions derived from the above
  GenerationWarning    → quality signal emitted at any pipeline stage
  GeneratedArtifact    → the final code output + metadata

NOTE: These are dataclasses / plain Python objects, not ORM models.
      ORM models (SQLAlchemy) will live in app/models/ when persistence is added.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


# ─── Enums (internal) ─────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class SelectorStrategy(str, Enum):
    """Stability ranking of selector strategies (high = more stable)."""
    data_testid = "data-testid"
    aria_role = "aria-role"
    aria_label = "aria-label"
    css_id = "css-id"
    css_class = "css-class"
    text = "text"
    xpath = "xpath"


class OutputFormat(str, Enum):
    playwright = "playwright"
    robot = "robot"


# ─── Domain models ────────────────────────────────────────────────────────────

@dataclass
class TestScenarioInput:
    """
    The user's intent, normalized and validated.
    Created from the HTTP request payload.
    """
    target_url: str
    requirements: str
    output_format: OutputFormat = OutputFormat.playwright


@dataclass
class SelectorCandidate:
    """
    A UI element on the target page with a proposed selector and confidence score.

    TODO: Populated by PageInspector. Ranked by SelectorStrategy stability.
    """
    element_type: str          # e.g. "button", "input", "link"
    visible_text: str | None   # visible label/text if any
    selector: str              # the proposed Playwright selector
    strategy: SelectorStrategy
    confidence: float          # 0.0 (fragile) → 1.0 (stable)
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class PageSnapshot:
    """
    Metadata captured by Playwright when inspecting the target URL.

    TODO: Populated by PageInspector.inspect_page().
    """
    url: str
    title: str
    interactive_elements: list[SelectorCandidate] = field(default_factory=list)
    # TODO: Add: forms, navigation structure, accessible headings, page text


@dataclass
class TestStep:
    """A single action or assertion in a test plan."""
    description: str           # human-readable step
    action: str                # e.g. "fill", "click", "assert_visible"
    selector: str | None       # target element selector
    value: str | None = None   # input value (for fill actions)


@dataclass
class TestPlan:
    """
    Structured intermediate representation of the test scenario.

    TODO: Produced by ScenarioPlanner from TestScenarioInput + PageSnapshot.
    Consumed by CodeGenerator to produce the final script.
    """
    title: str
    description: str
    steps: list[TestStep] = field(default_factory=list)
    # TODO: Add: preconditions, expected outcomes, tags


@dataclass
class GenerationWarning:
    """A quality signal emitted during any stage of the pipeline."""
    type: str          # e.g. "selector_fragile", "requirement_ambiguous"
    severity: str      # "info" | "warning" | "error"
    message: str
    element: str | None = None


@dataclass
class GeneratedArtifact:
    """The final output of the generation pipeline."""
    job_id: str
    output_format: OutputFormat
    code: str                  # the generated test script
    scenario_summary: str
    warnings: list[GenerationWarning] = field(default_factory=list)
    # TODO: Add: file_name, language, framework_version


@dataclass
class GenerationJob:
    """
    Tracks the full lifecycle of a generation request.

    Stored in the job repository. In the future, persisted to a database.
    """
    job_id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.pending
    input: TestScenarioInput | None = None
    artifact: GeneratedArtifact | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
