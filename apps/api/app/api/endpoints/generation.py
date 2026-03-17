"""
app/api/endpoints/generation.py

POST /api/v1/generate   — accepts multipart/form-data with optional file uploads
GET  /api/v1/jobs/{id}  — poll job status and result
"""

import asyncio

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.domain.models import UploadedFile
from app.schemas.generation import CreateJobResponse, JobResult
from app.services.generation_service import GenerationService

router = APIRouter()
_service = GenerationService()


@router.post(
    "/generate",
    response_model=CreateJobResponse,
    status_code=202,
    summary="Submit a generation request",
)
async def create_generation_job(
    target_url: str = Form(..., description="The URL of the web app to test"),
    requirements: str = Form(default="", description="Plain-English acceptance criteria"),
    output_format: str = Form(default="playwright"),
    requirement_files: list[UploadFile] = File(default=[]),
    screenshots: list[UploadFile] = File(default=[]),
) -> CreateJobResponse:
    """
    Create a generation job and return its ID immediately (non-blocking).
    The pipeline runs in the background — poll GET /api/v1/jobs/{job_id} for results.

    Accepts multipart/form-data:
    - target_url          string  (required)
    - requirements        string
    - output_format       playwright | robot
    - requirement_files   one or more .pdf / .docx / .md / .txt files
    - screenshots         one or more image files (png / jpg / webp)
    """
    # Read uploaded file bytes eagerly (UploadFile streams are not safe to read later)
    req_files: list[UploadedFile] = []
    for f in requirement_files:
        if f.filename:
            data = await f.read()
            req_files.append(UploadedFile(
                filename=f.filename,
                content_type=f.content_type or "application/octet-stream",
                data=data,
            ))

    shot_files: list[UploadedFile] = []
    for f in screenshots:
        if f.filename:
            data = await f.read()
            shot_files.append(UploadedFile(
                filename=f.filename,
                content_type=f.content_type or "image/png",
                data=data,
            ))

    job_response = await _service.create_job(
        target_url=target_url,
        requirements=requirements,
        output_format=output_format,
        requirement_files=req_files,
        screenshots=shot_files,
    )

    # Run the real pipeline in the background — response is returned immediately
    asyncio.create_task(_service.run_pipeline(job_response.job_id))

    return job_response


@router.get(
    "/jobs/{job_id}",
    response_model=JobResult,
    summary="Get job status and result",
)
async def get_job(job_id: str) -> JobResult:
    """Poll this endpoint after submitting a job. Returns current status + result."""
    result = await _service.get_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result
