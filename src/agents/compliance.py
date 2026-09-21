"""
Compliance Officer Agent and data-safety guardrail pipeline.

PII/PHI and legal-liability screening is now deterministic (regex-based, see
src/compliance/pii_redaction.py) rather than delegated to the LLM's own
judgment. This means: (1) the risk decision is auditable and doesn't depend
on the LLM correctly noticing something sensitive, and (2) when risk is
detected, zero patient content is sent to any third-party LLM - the halt
notice is a static, pre-translated template instead. When no risk is
detected, the (already-redacted, defense-in-depth) text is used to compose
the final report directly in the patient's detected language, so the
downstream voice_output_node's gTTS synthesis speaks the correct language.
"""

from typing import Any, Dict

from src.compliance.halt_templates import get_halt_message
from src.compliance.pii_redaction import redact_pii
from src.graph.state import SharedState
from src.llm.groq_client import GroqReasoningClient, LLMReasoningError, build_token_log
from src.voice.language_support import resolve_language_profile

_SYSTEM_PROMPT_TEMPLATE = (
    "You are a healthcare communications assistant. Compose a short, calm, "
    "professional patient-facing clinical verification report summarizing "
    "the provided (already PII-redacted) symptoms and diagnostic pathway. "
    "Respond ONLY with a JSON object of the exact shape: "
    '{{"patient_facing_report": "..."}}. '
    "Write the patient_facing_report field entirely in {language_name}, "
    "regardless of what language this prompt is written in."
)


class ComplianceAgent:
    """Screen for PII/legal risk deterministically, then compose the localized report.

    Prefers a Groq-backed LLM call for composing the final report text, once
    the risk decision has already been made in Python. Falls back to the
    original deterministic, English-only report template if no API key is
    configured or the LLM call fails.
    """

    def __init__(self) -> None:
        try:
            self._llm: GroqReasoningClient | None = GroqReasoningClient()
        except LLMReasoningError as exc:
            print(f"[AGENT] Compliance: LLM unavailable, using rule-based fallback ({exc})")
            self._llm = None

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """Audit raw input deterministically, then compile a safe, localized report."""
        print("[AGENT] Compliance Officer running deterministic PII/legal-risk scan...")
        redaction = redact_pii(state.raw_symptoms)
        profile, _ = resolve_language_profile(state.detected_language_code)

        if redaction.pii_detected or redaction.legal_risk_detected:
            status = f"FAILED: {'; '.join(redaction.reasons)}"
            print(
                f"[AGENT] Compliance BLOCKED - {status}. No patient content was "
                "sent to any LLM for this case; the halt notice is a static template."
            )
            token_log: Dict[str, Any] = {
                "node": "compliance_agent_pii_scan",
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
            }
            return {
                "compliance_status": status,
                "final_clinical_report": get_halt_message(profile.assemblyai_code),
                "current_step": "COMPLIANCE_AUDIT_COMPLETE",
                "token_usage_log": state.token_usage_log + [token_log],
            }

        if self._llm is not None:
            try:
                return await self._process_with_llm(state, redaction.redacted_text, profile)
            except LLMReasoningError as exc:
                print(f"[AGENT] Compliance LLM call failed, falling back to rules: {exc}")
        return self._process_with_rules(state)

    async def _process_with_llm(self, state: SharedState, redacted_text: str, profile: Any) -> Dict[str, Any]:
        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(language_name=profile.display_name)
        user_prompt = (
            f"Patient tracker ID: {state.patient_id}\n"
            f"Redacted patient statement: {redacted_text}\n"
            f"Extracted symptoms: {', '.join(state.extracted_symptoms) or 'None'}\n"
            f"Diagnostic pathway: {state.initial_diagnosis or 'Not yet determined'}"
        )
        parsed = await self._llm.complete_json(system_prompt, user_prompt)

        report = str(parsed.get("patient_facing_report") or "").strip()
        if not report:
            raise LLMReasoningError("LLM returned an empty patient_facing_report.")

        token_log = build_token_log("compliance_agent", parsed.get("_usage", {}))
        return {
            "compliance_status": "PASSED",
            "final_clinical_report": report,
            "current_step": "COMPLIANCE_AUDIT_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }

    def _process_with_rules(self, state: SharedState) -> Dict[str, Any]:
        """Original deterministic English-only fallback, used only when the risk
        scan already passed (see process()) but no LLM is available to localize
        the report.

        Note: this composes the report in English regardless of
        ``detected_language_code``. If the LLM path is down for a
        non-English patient, downstream gTTS synthesis will read this
        English text using the patient's language voice, which will sound
        wrong. This exists purely to keep the loop from crashing, not as a
        multilingual substitute for the LLM path.
        """
        compiled_report = (
            "FINAL CLINICAL REPORT\n"
            "=====================\n"
            f"Patient Tracker ID: {state.patient_id}\n"
            f"Symptoms Analysed: {', '.join(state.extracted_symptoms)}\n"
            f"Diagnostic Pathway: {state.initial_diagnosis}\n"
            "Status: Certified safe for clinical evaluation."
        )
        token_log: Dict[str, Any] = {
            "node": "compliance_agent_fallback",
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost": 0.0,
        }
        return {
            "compliance_status": "PASSED",
            "final_clinical_report": compiled_report,
            "current_step": "COMPLIANCE_AUDIT_COMPLETE_FALLBACK",
            "token_usage_log": state.token_usage_log + [token_log],
        }
