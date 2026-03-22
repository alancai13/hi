"""
app/repositories/job_store.py — In-memory job store

A simple dict-backed store for GenerationJob objects.

STATUS: Placeholder — intentionally in-memory only.
        Replace with a real persistence layer (PostgreSQL, Redis) before
        running more than one worker process or restarting the server.

TODO (Phase 4):
  - Replace with an async SQLAlchemy repository
  - Add a base AbstractJobRepository interface so the service layer is storage-agnostic
  - Add a Redis-backed implementation for fast status lookups
"""

from app.domain.models import GenerationJob


class InMemoryJobStore:
    """
    Thread-unsafe in-memory job store. Fine for single-process development.
    Not suitable for production or multi-worker deployments.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, GenerationJob] = {}

    async def save(self, job: GenerationJob) -> None:
        """Persist (or update) a job."""
        self._jobs[job.job_id] = job

    async def get(self, job_id: str) -> GenerationJob | None:
        """Retrieve a job by ID. Returns None if not found."""
        return self._jobs.get(job_id)

    async def list_all(self) -> list[GenerationJob]:
        """Return all jobs. For debugging only."""
        return list(self._jobs.values())

    async def delete(self, job_id: str) -> bool:
        """Remove a job. Returns True if it existed."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False


# Module-level singleton. Replace with dependency injection when the store
# needs to be swapped (e.g. test environment vs. production).
job_store = InMemoryJobStore()
