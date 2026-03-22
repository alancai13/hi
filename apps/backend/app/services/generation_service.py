"""
app/services/generation_service.py — Generation pipeline orchestrator

Pipeline stages:
  1. Create job + persist (synchronous — returns job_id to caller)
  2. run_pipeline() — called as asyncio.create_task, runs in background:
       a. PageInspector.inspect_page(url)      → PageSnapshot
       b. CodeGenerator.generate(job, snap)    → GeneratedArtifact  (calls Gemini)
       c. Persist artifact, mark job completed
"""

from datetime import datetime

from app.core.logging import get_logger
from app.domain.models import (
    GenerationJob,
    JobStatus,
    OutputFormat,
    TestScenarioInput,
    UploadedFile,
)
from app.repositories.job_store import job_store
from app.schemas.generation import (
    CreateJobResponse,
    JobResult,
)
from app.schemas.generation import GenerationWarning as WarningSchema
from app.schemas.generation import JobStatus as JobStatusSchema
from app.schemas.generation import OutputFormat as OutputFormatSchema
from app.services.code_generator import CodeGenerator
from app.services.page_inspector import PageInspector

logger = get_logger(__name__)


class GenerationService:
    """Coordinates job lifecycle and delegates to pipeline services."""

    def __init__(self) -> None:
        self.inspector = PageInspector()
        self.generator = CodeGenerator()

    # ─── Public API ───────────────────────────────────────────────────────────

    async def create_job(
        self,
        target_url: str,
        requirements: str,
        output_format: str,
        requirement_files: list[UploadedFile],
        screenshots: list[UploadedFile],
    ) -> CreateJobResponse:
        """
        Validate input, persist a new job, and return its ID.
        Does NOT start the pipeline — caller does asyncio.create_task(run_pipeline).
        """
        scenario_input = TestScenarioInput(
            target_url=target_url,
            requirements=requirements,
            output_format=(
                OutputFormat(output_format)
                if output_format in OutputFormat._value2member_map_
                else OutputFormat.playwright
            ),
        )

        job = GenerationJob(
            input=scenario_input,
            requirement_files=requirement_files,
            screenshots=screenshots,
        )
        await job_store.save(job)

        logger.info(
            "Job %s created | url=%s | req_files=%d | screenshots=%d",
            job.job_id,
            target_url,
            len(requirement_files),
            len(screenshots),
        )

        return CreateJobResponse(job_id=job.job_id, created_at=job.created_at)

    async def get_job(self, job_id: str) -> JobResult | None:
        """Retrieve a job and map to the API response schema."""
        job = await job_store.get(job_id)
        return self._map_to_result(job) if job else None

    async def run_pipeline(self, job_id: str) -> None:
        """
        Full generation pipeline. Called as an asyncio background task.

        Steps:
          1. Page inspection via Playwright
          2. Test generation via Gemini
        """
        job = await job_store.get(job_id)
        if job is None or job.input is None:
            logger.error("run_pipeline: job %s not found", job_id)
            return

        # ── Mark as running ───────────────────────────────────────────────────
        job.status = JobStatus.running
        await job_store.save(job)

        try:
            # ── Step 1: Inspect the page ──────────────────────────────────────
            logger.info("[%s] Step 1/2 — inspecting %s", job_id, job.input.target_url)
            snapshot = await self.inspector.inspect_page(job.input.target_url)

            # ── Step 2: Generate the test script ──────────────────────────────
            logger.info("[%s] Step 2/2 — calling Gemini", job_id)
            artifact = await self.generator.generate(job, snapshot)

            # ── Mark as completed ─────────────────────────────────────────────
            job.artifact = artifact
            job.status = JobStatus.completed
            job.completed_at = datetime.utcnow()
            logger.info("[%s] Pipeline completed successfully", job_id)

        except Exception as exc:
            logger.exception("[%s] Pipeline failed: %s", job_id, exc)
            job.status = JobStatus.failed
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()

        await job_store.save(job)

    # ─── Mapping ──────────────────────────────────────────────────────────────

    def _map_to_result(self, job: GenerationJob) -> JobResult:
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
