"""
app/services/artifact_exporter.py — Artifact export service

Handles converting a GeneratedArtifact to a downloadable format.
In the current skeleton this is trivially simple — just the code string.

STATUS: Stub — minimal implementation.

TODO (Phase 3+):
  - Write artifacts to a temp file or object storage (S3/GCS)
  - Return a signed download URL or a file stream
  - Support multiple export formats (.spec.ts, .robot, .zip with fixtures)
  - Add metadata headers (filename, content-type, size)
"""

from app.core.logging import get_logger
from app.domain.models import GeneratedArtifact, OutputFormat

logger = get_logger(__name__)

_CONTENT_TYPES: dict[OutputFormat, str] = {
    OutputFormat.playwright: "application/typescript",
    OutputFormat.robot: "text/plain",
}

_FILE_EXTENSIONS: dict[OutputFormat, str] = {
    OutputFormat.playwright: ".spec.ts",
    OutputFormat.robot: ".robot",
}


class ArtifactExporter:
    """Converts a GeneratedArtifact into an exportable form."""

    def get_filename(self, artifact: GeneratedArtifact) -> str:
        """Return a suggested filename for the artifact."""
        ext = _FILE_EXTENSIONS.get(artifact.output_format, ".txt")
        # Sanitise the summary to create a slug
        slug = artifact.scenario_summary[:40].lower().replace(" ", "_").replace("/", "_")
        slug = "".join(c for c in slug if c.isalnum() or c == "_")
        return f"testgen_{slug}{ext}"

    def get_content_type(self, artifact: GeneratedArtifact) -> str:
        """Return the MIME content type for the artifact."""
        return _CONTENT_TYPES.get(artifact.output_format, "text/plain")

    def get_code(self, artifact: GeneratedArtifact) -> str:
        """Return the raw code string."""
        return artifact.code

    # TODO: async def upload_to_storage(self, artifact: GeneratedArtifact) -> str:
    #       """Upload artifact to S3/GCS and return a download URL."""
