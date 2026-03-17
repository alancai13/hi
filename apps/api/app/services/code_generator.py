"""
app/services/code_generator.py — Code generation service

Translates a structured TestPlan into executable test code.

Designed to support multiple output formats via a strategy pattern.
Currently only PlaywrightGenerator exists (as a stub).

STATUS: Stub — not implemented.

TODO (Phase 1):
  - Implement PlaywrightGenerator using Jinja2 or simple string templating
  - Map TestStep.action values to Playwright API calls
  - Handle selector quoting, async/await, imports, test structure

TODO (Phase 3):
  - Implement RobotFrameworkGenerator
  - Abstract BaseCodeGenerator interface so formats are pluggable
"""

from app.core.logging import get_logger
from app.domain.models import (
    GeneratedArtifact,
    GenerationWarning,
    OutputFormat,
    TestPlan,
)

logger = get_logger(__name__)


class CodeGenerator:
    """
    Dispatches to the appropriate format-specific generator based on OutputFormat.
    """

    def __init__(self) -> None:
        self._generators: dict[OutputFormat, "BaseCodeGenerator"] = {
            OutputFormat.playwright: PlaywrightGenerator(),
            # OutputFormat.robot: RobotFrameworkGenerator(),  # future
        }

    async def generate(
        self,
        plan: TestPlan,
        job_id: str,
        output_format: OutputFormat = OutputFormat.playwright,
    ) -> GeneratedArtifact:
        """
        Generate a test script artifact from a TestPlan.

        Args:
            plan: The structured test plan from ScenarioPlanner.
            job_id: The parent generation job ID.
            output_format: Target framework.

        Returns:
            GeneratedArtifact containing the code and metadata.
        """
        generator = self._generators.get(output_format)
        if generator is None:
            raise ValueError(f"No generator registered for format: {output_format}")

        return await generator.generate(plan, job_id)


class BaseCodeGenerator:
    """
    Abstract base for format-specific generators.
    TODO: Convert to ABC (abc.ABC) when multiple implementations exist.
    """

    async def generate(self, plan: TestPlan, job_id: str) -> GeneratedArtifact:
        raise NotImplementedError


class PlaywrightGenerator(BaseCodeGenerator):
    """
    Generates Playwright Test (TypeScript) code from a TestPlan.

    TODO (Phase 1): Implement using Jinja2 templates or string construction.
    """

    async def generate(self, plan: TestPlan, job_id: str) -> GeneratedArtifact:
        """
        Convert a TestPlan into a Playwright .spec.ts file.

        TODO: Implement. Currently returns a stub artifact.
        """
        logger.info("PlaywrightGenerator.generate() — not yet implemented, returning stub")

        # TODO: Use a template engine (Jinja2) to render the script.
        # For each step in plan.steps, emit the appropriate Playwright call:
        #   goto → await page.goto(url)
        #   fill → await page.fill(selector, value)
        #   click → await page.click(selector)
        #   assert_visible → await expect(page.locator(selector)).toBeVisible()
        #   assert_url → await expect(page).toHaveURL(url)

        stub_code = f"// TODO: Generated Playwright script for '{plan.title}'\n"
        stub_warnings: list[GenerationWarning] = []

        return GeneratedArtifact(
            job_id=job_id,
            output_format=OutputFormat.playwright,
            code=stub_code,
            scenario_summary=plan.description,
            warnings=stub_warnings,
        )


# Future:
# class RobotFrameworkGenerator(BaseCodeGenerator):
#     """Generates Robot Framework Browser library scripts from a TestPlan."""
#     async def generate(self, plan: TestPlan, job_id: str) -> GeneratedArtifact: ...
