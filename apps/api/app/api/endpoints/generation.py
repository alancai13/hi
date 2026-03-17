"""
app/api/endpoints/generation.py — Test generation endpoints

POST /api/v1/generate   — submit a generation request, returns a job ID
GET  /api/v1/jobs/{id}  — poll job status and retrieve the result
"""

from fastapi import APIRouter, HTTPException

from app.schemas.generation import CreateJobResponse, GenerationRequest, JobResult
from app.services.generation_service import GenerationService

router = APIRouter()

# Dependency: the service layer.
# TODO: Replace with FastAPI Depends() injection when the service has real dependencies.
_service = GenerationService()


@router.post(
    "/generate",
    response_model=CreateJobResponse,
    status_code=202,
    summary="Submit a generation request",
)
async def create_generation_job(request: GenerationRequest) -> CreateJobResponse:
    """
    Accept a URL and plain-English requirements, create a generation job, and
    return its ID immediately.

    The actual generation pipeline runs asynchronously (stubbed for now).
    Poll GET /api/v1/jobs/{job_id} for status and results.
    """
    job = await _service.create_job(request)
    return job


@router.get(
    "/jobs/{job_id}",
    response_model=JobResult,
    summary="Get job status and result",
)
async def get_job(job_id: str) -> JobResult:
    """
    Retrieve the current status and result of a generation job.

    Returns the job as-is, including:
    - status (pending / running / completed / failed)
    - scenario_summary (once available)
    - generated_code (once available)
    - warnings (selector confidence, ambiguous requirements, etc.)
    """
    result = await _service.get_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result
