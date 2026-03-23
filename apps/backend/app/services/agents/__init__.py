"""
app/services/agents/ — Six-stage test generation agent pipeline.

Stage 1: IntakeAgent      — normalise URL + requirements into structured intent
Stage 2: PageInspector    — Playwright DOM capture (lives in services/page_inspector.py)
Stage 3: PlanningAgent    — LLM produces a structured TestPlan JSON
Stage 4: CodegenAgent     — template rendering of TestPlan → TypeScript (no LLM)
Stage 5: ValidationAgent  — static analysis of rendered code (no LLM)
Stage 6: RepairAgent      — LLM fixes TestPlan when validation finds errors

Orchestration lives in app/services/generation_service.run_pipeline().
"""
