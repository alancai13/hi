"""
app/services/generation_service.py — Generation pipeline orchestrator

Coordinates the full generation pipeline:
  1. Validate and normalize input → TestScenarioInput
  2. Create a GenerationJob and persist it
  3. Trigger pipeline execution (async in future)
  4. Return job state to the API layer

The actual pipeline steps are delegated to specialist service modules.
This service intentionally knows nothing about HTTP — it works with domain models only.

TODO (Phase 1):
  - Replace mock pipeline with real orchestration
  - Move pipeline execution to a background task (asyncio.create_task or Celery)
  - Add proper error handling and job failure states
"""

from datetime import datetime

from app.core.logging import get_logger
from app.domain.models import (
    GeneratedArtifact,
    GenerationJob,
    GenerationWarning,
    JobStatus,
    OutputFormat,
    TestScenarioInput,
)
from app.repositories.job_store import job_store
from app.schemas.generation import (
    CreateJobResponse,
    GenerationRequest,
    JobResult,
)
from app.schemas.generation import GenerationWarning as WarningSchema
from app.schemas.generation import JobStatus as JobStatusSchema
from app.schemas.generation import OutputFormat as OutputFormatSchema
from app.services.artifact_exporter import ArtifactExporter
from app.services.code_generator import CodeGenerator
from app.services.page_inspector import PageInspector
from app.services.scenario_planner import ScenarioPlanner
from app.services.script_validator import ScriptValidator

logger = get_logger(__name__)


class GenerationService:
    """
    Orchestrates the end-to-end generation pipeline.

    Currently: creates a job and immediately returns mock placeholder data
    so the frontend can render a realistic result shape.

    Future: runs the real pipeline asynchronously and updates job state.
    """

    def __init__(self) -> None:
        self.inspector = PageInspector()
        self.planner = ScenarioPlanner()
        self.generator = CodeGenerator()
        self.validator = ScriptValidator()
        self.exporter = ArtifactExporter()

    async def create_job(self, request: GenerationRequest) -> CreateJobResponse:
        """
        Validate input, create a job, and kick off generation.
        Returns the job ID immediately (non-blocking).
        """
        scenario_input = TestScenarioInput(
            target_url=str(request.target_url),
            requirements=request.requirements,
            output_format=OutputFormat(request.output_format.value),
        )

        job = GenerationJob(input=scenario_input)
        await job_store.save(job)

        logger.info("Created generation job %s for URL %s", job.job_id, scenario_input.target_url)

        # TODO: Replace with asyncio.create_task(self._run_pipeline(job.job_id))
        #       or enqueue to a Celery/ARQ task queue.
        await self._run_mock_pipeline(job.job_id)

        return CreateJobResponse(job_id=job.job_id, created_at=job.created_at)

    async def get_job(self, job_id: str) -> JobResult | None:
        """Retrieve a job and map it to the API response schema."""
        job = await job_store.get(job_id)
        if job is None:
            return None
        return self._map_to_result(job)

    # ─── Mock pipeline (temporary) ────────────────────────────────────────────

    async def _run_mock_pipeline(self, job_id: str) -> None:
        """
        Placeholder pipeline that immediately marks the job as completed with
        canned data. This makes the UI understandable before real logic exists.

        TODO: Delete this method and replace with _run_real_pipeline().
        """
        job = await job_store.get(job_id)
        if job is None:
            return

        job.status = JobStatus.completed
        job.completed_at = datetime.utcnow()
        job.artifact = GeneratedArtifact(
            job_id=job_id,
            output_format=job.input.output_format if job.input else OutputFormat.playwright,
            scenario_summary=(
                "Login flow: navigate to login page → enter credentials "
                "→ submit form → assert redirect to dashboard"
            ),
            code=_PLACEHOLDER_PLAYWRIGHT_SCRIPT,
            warnings=[
                GenerationWarning(
                    type="selector_fragile",
                    severity="warning",
                    message=(
                        "Login button was matched by visible text. "
                        "Consider adding a data-testid attribute for stability."
                    ),
                    element="button:has-text('Log in')",
                )
            ],
        )
        await job_store.save(job)
        logger.info("Mock pipeline completed for job %s", job_id)

    # ─── Real pipeline (future) ───────────────────────────────────────────────

    async def _run_real_pipeline(self, job_id: str) -> None:
        """
        Full generation pipeline. Replace _run_mock_pipeline with this.

        TODO (Phase 1): Implement each step.
        """
        job = await job_store.get(job_id)
        if job is None or job.input is None:
            return

        try:
            job.status = JobStatus.running
            await job_store.save(job)

            # Step 1 — Inspect the page
            # page_snapshot = await self.inspector.inspect_page(job.input.target_url)

            # Step 2 — Build a test plan
            # test_plan = await self.planner.build_test_plan(job.input, page_snapshot)

            # Step 3 — Generate code
            # artifact = await self.generator.generate(test_plan, job.input.output_format)

            # Step 4 — Validate (optional)
            # validation_result = await self.validator.validate(artifact, job.input.target_url)

            # Step 5 — Finalize
            # job.artifact = artifact
            job.status = JobStatus.completed
            job.completed_at = datetime.utcnow()

        except Exception as exc:
            logger.exception("Pipeline failed for job %s: %s", job_id, exc)
            job.status = JobStatus.failed
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()

        await job_store.save(job)

    # ─── Mapping ──────────────────────────────────────────────────────────────

    def _map_to_result(self, job: GenerationJob) -> JobResult:
        """Map a domain GenerationJob to the API response schema."""
        warnings: list[WarningSchema] = []
        generated_code = None
        scenario_summary = None

        if job.artifact:
            generated_code = job.artifact.code
            scenario_summary = job.artifact.scenario_summary
            warnings = [
                WarningSchema(
                    type=w.type,  # type: ignore[arg-type]
                    severity=w.severity,  # type: ignore[arg-type]
                    message=w.message,
                    element=w.element,
                )
                for w in job.artifact.warnings
            ]

        return JobResult(
            job_id=job.job_id,
            status=JobStatusSchema(job.status.value),
            created_at=job.created_at,
            completed_at=job.completed_at,
            scenario_summary=scenario_summary,
            warnings=warnings,
            generated_code=generated_code,
            output_format=OutputFormatSchema(
                job.input.output_format.value if job.input else "playwright"
            ),
            error_message=job.error_message,
        )


# ─── Placeholder script ───────────────────────────────────────────────────────
# Shown in the UI before the real generator is implemented.

_PLACEHOLDER_PLAYWRIGHT_SCRIPT = """\
import { test, expect } from '@playwright/test';

// Generated by TestGen — placeholder script
// TODO: Replace with real generated output from the pipeline

test('Login flow', async ({ page }) => {
  // Navigate to the target URL
  await page.goto('https://example.com/login');

  // Fill in credentials
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');

  // Submit the form
  // NOTE: selector_fragile warning — consider adding data-testid to the button
  await page.click('button:has-text(\\'Log in\\')');

  // Assert redirect to dashboard
  await expect(page).toHaveURL('/dashboard');

  // Assert welcome message is visible
  await expect(page.getByText('Welcome')).toBeVisible();
});
"""
