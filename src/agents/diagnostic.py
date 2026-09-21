"""Diagnostic reasoning agent: LLM-backed Tree of Thoughts with a rule-based fallback."""

from typing import Any, Dict, List

from src.graph.state import SharedState
from src.llm.groq_client import GroqReasoningClient, LLMReasoningError, build_token_log

_SYSTEM_PROMPT = (
    "You are a clinical decision-support assistant performing a structured "
    "Tree-of-Thoughts evaluation. This is decision support only, never a "
    "final diagnosis. Given the extracted symptoms, any supporting research "
    "context, and any prior critic feedback from a previous iteration, "
    "propose exactly 3 distinct candidate diagnostic/management paths and "
    "score each from 0 to 10 on clinical confidence (specificity of match to "
    "symptoms, safety of the recommended path, and consistency with the "
    "research context). If prior critic feedback is present, your paths must "
    "visibly account for it. Respond ONLY with a JSON object of the exact "
    'shape: {"branches": [{"path": "...", "confidence_score": 0-10}, '
    '{"path": "...", "confidence_score": 0-10}, {"path": "...", '
    '"confidence_score": 0-10}]}. Every path description must end with a '
    "note that clinician review is required before acting on it."
)


class DiagnosticAgent:
    """Score alternative clinical paths and select the highest-confidence path.

    Prefers a Groq-backed LLM call for real Tree-of-Thoughts reasoning over
    the extracted symptoms and research context. Falls back to the original
    deterministic static branches if no API key is configured or the LLM
    call fails, preserving the existing self-healing retry contract
    (``retry_count`` / ``critic_feedback``) either way.
    """

    def __init__(self) -> None:
        try:
            self._llm: GroqReasoningClient | None = GroqReasoningClient()
        except LLMReasoningError as exc:
            print(f"[AGENT] Diagnostic: LLM unavailable, using rule-based fallback ({exc})")
            self._llm = None

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """Evaluate candidate reasoning branches and compile a diagnosis artifact."""
        print(
            f"[AGENT] Diagnostic evaluating case state (Retry Iteration: {state.retry_count})..."
        )
        if self._llm is not None:
            try:
                return await self._process_with_llm(state)
            except LLMReasoningError as exc:
                print(f"[AGENT] Diagnostic LLM call failed, falling back to rules: {exc}")
        return self._process_with_rules(state)

    async def _process_with_llm(self, state: SharedState) -> Dict[str, Any]:
        symptoms = ", ".join(state.extracted_symptoms) or "General_Observation"
        user_prompt = (
            f"Extracted symptoms: {symptoms}\n"
            f"Retry iteration: {state.retry_count}\n"
            f"Prior critic feedback: {state.critic_feedback or 'None yet.'}\n"
            f"Supporting research context: {state.medical_research_data or 'None provided.'}"
        )
        parsed = await self._llm.complete_json(_SYSTEM_PROMPT, user_prompt)

        branches = parsed.get("branches")
        if not isinstance(branches, list) or not branches:
            raise LLMReasoningError("LLM response contained no diagnostic branches.")

        try:
            best = max(branches, key=lambda branch: float(branch.get("confidence_score", 0)))
        except (TypeError, ValueError) as exc:
            raise LLMReasoningError(f"LLM returned malformed branch scores: {exc}") from exc

        compiled_diagnosis = (
            f"Selected Path: {best.get('path', 'Unspecified path')} "
            f"(Confidence Evaluation: {best.get('confidence_score', 0)}/10)"
        )
        try:
            confidence_value = float(best.get("confidence_score", 0))
        except (TypeError, ValueError):
            confidence_value = 0.0
        token_log = build_token_log("diagnostic_agent", parsed.get("_usage", {}))
        return {
            "initial_diagnosis": compiled_diagnosis,
            "diagnostic_confidence": confidence_value,
            "current_step": "DIAGNOSIS_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }

    def _process_with_rules(self, state: SharedState) -> Dict[str, Any]:
        """Original deterministic static-branch fallback, kept as a safety net."""
        thoughts_branches: List[Dict[str, Any]] = [
            {"path": "Path A: Standard Pharmacotherapy approach.", "confidence_score": 8.5},
            {"path": "Path B: Alternative holistic lifestyle adaptation loop.", "confidence_score": 6.2},
            {"path": "Path C: Wait-and-see conservative diagnostic profiling.", "confidence_score": 5.0},
        ]

        if state.retry_count > 0:
            thoughts_branches[0]["path"] = (
                f"{thoughts_branches[0]['path']} Adjusted dynamically via Critic Feedback: "
                f"{state.critic_feedback}"
            )
            thoughts_branches[0]["confidence_score"] = 9.2

        best_branch = max(thoughts_branches, key=lambda branch: float(branch["confidence_score"]))
        compiled_diagnosis = (
            f"Selected Path: {best_branch['path']} "
            f"(Confidence Evaluation: {best_branch['confidence_score']}/10)"
        )
        token_log: Dict[str, Any] = {
            "node": "diagnostic_agent_fallback",
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost": 0.0,
        }
        return {
            "initial_diagnosis": compiled_diagnosis,
            "diagnostic_confidence": float(best_branch["confidence_score"]),
            "current_step": "DIAGNOSIS_COMPLETE_FALLBACK",
            "token_usage_log": state.token_usage_log + [token_log],
        }
