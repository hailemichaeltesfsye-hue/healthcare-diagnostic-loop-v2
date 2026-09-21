"""Triage parsing and structural symptom extraction agent node."""

from typing import Any, Dict, List

from src.compliance.pii_redaction import redact_pii
from src.graph.state import SharedState
from src.llm.groq_client import GroqReasoningClient, LLMReasoningError, build_token_log
from src.voice.language_support import resolve_language_profile

_SYSTEM_PROMPT = (
    "You are a clinical triage assistant. The patient statement you are given "
    "may be written in any language - read it in its original language, do "
    "not ask for translation. Extract normalized, concise clinical symptom "
    "or condition labels (e.g. Hypertension, Migraine, Diabetes, Insomnia). "
    "Respond ONLY with a JSON object of the exact shape: "
    '{"extracted_symptoms": ["Label_One", "Label_Two", ...]}. '
    'If no clear symptom is stated, respond with {"extracted_symptoms": '
    '["General_Observation"]}. Do not include any text outside the JSON object.'
)


class TriageAgent:
    """Extract unstructured patient descriptions into normalized symptom labels.

    Prefers a Groq-backed LLM call so it can correctly parse symptoms in any
    of the loop's supported languages (English, Amharic, Arabic, Chinese,
    French, Hindi). Falls back to the original deterministic English-keyword
    rules if no API key is configured or the LLM call fails, so a transient
    outage degrades the loop instead of breaking it.
    """

    def __init__(self) -> None:
        try:
            self._llm: GroqReasoningClient | None = GroqReasoningClient()
        except LLMReasoningError as exc:
            print(f"[AGENT] Triage: LLM unavailable, using rule-based fallback ({exc})")
            self._llm = None

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """Analyze raw symptoms and return a LangGraph-compatible partial update."""
        print("[AGENT] Triage processing raw inputs...")
        if self._llm is not None:
            try:
                return await self._process_with_llm(state)
            except LLMReasoningError as exc:
                print(f"[AGENT] Triage LLM call failed, falling back to rules: {exc}")
        return self._process_with_rules(state)

    async def _process_with_llm(self, state: SharedState) -> Dict[str, Any]:
        profile, _ = resolve_language_profile(state.detected_language_code)
        # Redact before this ever reaches a third-party LLM. Compliance runs
        # later in the pipeline and would be too late to prevent this leak.
        redacted_statement = redact_pii(state.raw_symptoms).redacted_text
        user_prompt = (
            f"Patient-reported symptoms (spoken language: {profile.display_name}):\n"
            f"{redacted_statement}"
        )
        parsed = await self._llm.complete_json(_SYSTEM_PROMPT, user_prompt)

        extracted = parsed.get("extracted_symptoms")
        if not isinstance(extracted, list) or not extracted:
            extracted = ["General_Observation"]
        extracted = [str(item).strip() for item in extracted if str(item).strip()]
        if not extracted:
            extracted = ["General_Observation"]

        token_log = build_token_log("triage_agent", parsed.get("_usage", {}))
        return {
            "extracted_symptoms": extracted,
            "current_step": "TRIAGE_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }

    def _process_with_rules(self, state: SharedState) -> Dict[str, Any]:
        """Original deterministic English-keyword fallback.

        Note: this only recognizes English keywords. If the LLM path is down
        and the patient spoke a non-English language, this fallback will
        almost always land on "General_Observation" - it exists purely as a
        safety net so the loop keeps running, not as a substitute for the
        LLM path in multilingual use.
        """
        raw = state.raw_symptoms.casefold()
        extracted: List[str] = []

        if "pressure" in raw or "headache" in raw or "hypertension" in raw:
            extracted.append("Hypertension")
        if "sugar" in raw or "diabetes" in raw or "thirst" in raw:
            extracted.append("Diabetes")
        if "migraine" in raw or "throbbing" in raw:
            extracted.append("Migraine")
        if "sleep" in raw or "insomnia" in raw:
            extracted.append("Insomnia")

        if not extracted:
            extracted.append("General_Observation")

        token_log: Dict[str, Any] = {
            "node": "triage_agent_fallback",
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost": 0.0,
        }
        return {
            "extracted_symptoms": extracted,
            "current_step": "TRIAGE_COMPLETE_FALLBACK",
            "token_usage_log": state.token_usage_log + [token_log],
        }
