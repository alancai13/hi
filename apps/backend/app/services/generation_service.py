"""
app/services/generation_service.py — Generation pipeline orchestrator

6-stage multi-agent pipeline:
  Stage 1 — IntakeAgent:      normalise URL + requirements → IntakeResult
  Stage 2 — PageInspector:    Playwright DOM capture → PageSnapshot
  Stage 3 — PlanningAgent:    LLM reasoning → TestPlan (structured JSON)
  Stage 4 — CodegenAgent:     template rendering → TypeScript (no LLM)
  Stage 5 — ValidationAgent:  static analysis → ValidationResult (no LLM)
  Stage 6 — RepairAgent:      LLM fixes the plan if validation fails (≤2 attempts)
"""

from datetime import datetime

from app.core.logging import get_logger
from app.domain.models import (
    GeneratedArtifact,
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
from app.services.agents.codegen_agent import CodegenAgent
from app.services.agents.intake_agent import IntakeAgent
from app.services.agents.planning_agent import PlanningAgent
from app.services.agents.repair_agent import RepairAgent
from app.services.agents.validation_agent import ValidationAgent
from app.services.page_inspector import PageInspector

logger = get_logger(__name__)

_MAX_REPAIR_ATTEMPTS = 2


class GenerationService:
    """Coordinates job lifecycle and runs the 6-stage agent pipeline."""

    def __init__(self) -> None:
        self.inspector = PageInspector()
        self.intake = IntakeAgent()
        self.planner = PlanningAgent()
        self.codegen = CodegenAgent()
        self.validator = ValidationAgent()
        self.repair = RepairAgent()

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
        Full 6-stage generation pipeline. Called as an asyncio background task.
        """
        job = await job_store.get(job_id)
        if job is None or job.input is None:
            logger.error("run_pipeline: job %s not found", job_id)
            return

        job.status = JobStatus.running
        await job_store.save(job)

        try:
            target_url = job.input.target_url
            requirements = job.input.requirements or ""

            # ── Stage 1: Intake ───────────────────────────────────────────────
            logger.info("[%s] Stage 1/6 — intake", job_id)
            intake = await self.intake.run(target_url, requirements)

            # ── Stage 2: Page inspection ──────────────────────────────────────
            logger.info("[%s] Stage 2/6 — inspecting %s", job_id, target_url)
            snapshot = await self.inspector.inspect_page(target_url)

            # ── Stage 3: Planning ─────────────────────────────────────────────
            logger.info("[%s] Stage 3/6 — planning", job_id)
            plan = await self.planner.run(intake, snapshot)

            # ── Stage 4 → 5 → 6 loop: Codegen → Validate → Repair ────────────
            code = self.codegen.run(plan)
            validation = self.validator.run(code)

            for attempt in range(1, _MAX_REPAIR_ATTEMPTS + 1):
                if not validation.has_errors:
                    break
                logger.info(
                    "[%s] Stage 6 — repair attempt %d/%d (%d errors)",
                    job_id,
                    attempt,
                    _MAX_REPAIR_ATTEMPTS,
                    sum(1 for i in validation.issues if i.severity == "error"),
                )
                plan = await self.repair.run(plan, validation)
                code = self.codegen.run(plan)
                validation = self.validator.run(code)

            artifact = GeneratedArtifact(
                job_id=job_id,
                output_format=job.input.output_format,
                code=code,
                scenario_summary=plan.description,
                warnings=[],
            )

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
