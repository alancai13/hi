"""
app/services/scenario_planner.py — Scenario planning service

Combines the user's plain-English requirements with the page snapshot to build
a structured TestPlan — an ordered sequence of steps and assertions.

STATUS: Stub — not implemented.

TODO (Phase 1 — rule-based):
  - Parse requirements text to identify action keywords (log in, click, fill, navigate, verify)
  - Map keywords to TestStep actions
  - Match steps to SelectorCandidates from the PageSnapshot
  - Emit GenerationWarning for ambiguous or unmatched requirements

TODO (Phase 2 — LLM-assisted):
  - Send requirements + page snapshot to an LLM (Claude/GPT)
  - Parse structured TestPlan from the LLM response
  - Use rule-based planner as a fallback
"""

from app.core.logging import get_logger
from app.domain.models import (
    GenerationWarning,
    PageSnapshot,
    TestPlan,
    TestScenarioInput,
    TestStep,
)

logger = get_logger(__name__)


class ScenarioPlanner:
    """
    Translates user requirements + page structure into a structured TestPlan.

    The TestPlan is the intermediate representation consumed by CodeGenerator.
    Keeping planning and code generation separate allows either to be improved
    independently — e.g. swapping to LLM planning without changing the generator.
    """

    async def build_test_plan(
        self,
        scenario_input: TestScenarioInput,
        page_snapshot: PageSnapshot,
    ) -> tuple[TestPlan, list[GenerationWarning]]:
        """
        Build a structured test plan from user requirements and page snapshot.

        Args:
            scenario_input: Normalized user input (URL + requirements).
            page_snapshot:  What Playwright found on the target page.

        Returns:
            (TestPlan, warnings) — the plan and any quality warnings.

        TODO: Implement. Currently returns a stub plan.
        """
        logger.info(
            "build_test_plan() called for %s — not yet implemented, returning stub",
            scenario_input.target_url,
        )

        # ── Stub response ─────────────────────────────────────────────────────
        stub_plan = TestPlan(
            title="[Stub] Test plan not yet generated",
            description=scenario_input.requirements,
            steps=[
                TestStep(
                    description="Navigate to target URL",
                    action="goto",
                    selector=None,
                    value=scenario_input.target_url,
                ),
                # TODO: Parse requirements and generate real steps
            ],
        )
        stub_warnings: list[GenerationWarning] = [
            GenerationWarning(
                type="requirement_ambiguous",
                severity="info",
                message="Scenario planner is not yet implemented. Steps are placeholders.",
            )
        ]
        return stub_plan, stub_warnings

    # TODO: Add helpers:
    # def _extract_action_keywords(self, requirements: str) -> list[str]: ...
    # def _match_step_to_selector(self, step_desc: str, candidates: list[SelectorCandidate]) -> ...:
    #     ...
    # async def _call_llm(self, prompt: str) -> str: ...
