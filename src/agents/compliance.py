"""Compliance Officer Agent and data-safety guardrail pipeline.

PII/PHI and legal-liability screening is deterministic. When no risk is
detected, the final patient-facing report is generated in the detected
clinical language. If the LLM is unavailable, a deterministic localized
fallback is used for all supported languages.
"""

from __future__ import annotations

from typing import Any, Dict

from src.compliance.halt_templates import get_halt_message
from src.compliance.pii_redaction import redact_pii
from src.graph.state import SharedState
from src.llm.groq_client import (
    GroqReasoningClient,
    LLMReasoningError,
    build_token_log,
)
from src.voice.language_support import resolve_language_profile


_SYSTEM_PROMPT_TEMPLATE = (
    "You are a healthcare communications assistant. "
    "Compose a short, calm, professional patient-facing clinical "
    "verification report summarizing the provided already-PII-redacted "
    "symptoms and diagnostic pathway. "
    "Respond ONLY with a JSON object of the exact shape: "
    '{{"patient_facing_report": "..."}}. '
    "The patient-facing report MUST be written entirely in "
    "{language_name} using language code {language_code}. "
    "Do NOT write the report in English. "
    "Do NOT include English headings, explanations, or translations. "
    "Preserve the clinical meaning of the supplied information."
)


_LOCALIZED_FALLBACKS: dict[str, dict[str, str]] = {
    "en": {
        "title": "FINAL CLINICAL REPORT",
        "tracker": "Patient Tracker ID",
        "symptoms": "Symptoms Analysed",
        "diagnosis": "Diagnostic Pathway",
        "status": "Status: Certified safe for clinical evaluation.",
    },
    "am": {
        "title": "የመጨረሻ የሕክምና ሪፖርት",
        "tracker": "የታካሚ መከታተያ መለያ",
        "symptoms": "የተመረመሩ ምልክቶች",
        "diagnosis": "የምርመራ ሂደት",
        "status": "ሁኔታ፦ ለሕክምና ግምገማ ደህንነቱ ተረጋግጧል።",
    },
    "ar": {
        "title": "التقرير السريري النهائي",
        "tracker": "معرّف متابعة المريض",
        "symptoms": "الأعراض التي تم تحليلها",
        "diagnosis": "مسار التشخيص",
        "status": "الحالة: تم اعتماد السلامة للتقييم السريري.",
    },
    "zh": {
        "title": "最终临床报告",
        "tracker": "患者追踪编号",
        "symptoms": "已分析的症状",
        "diagnosis": "诊断路径",
        "status": "状态：已确认可进行临床评估。",
    },
    "fr": {
        "title": "RAPPORT CLINIQUE FINAL",
        "tracker": "Identifiant de suivi du patient",
        "symptoms": "Symptômes analysés",
        "diagnosis": "Parcours diagnostique",
        "status": "Statut : jugé sûr pour l’évaluation clinique.",
    },
    "hi": {
        "title": "अंतिम चिकित्सीय रिपोर्ट",
        "tracker": "रोगी ट्रैकर आईडी",
        "symptoms": "विश्लेषित लक्षण",
        "diagnosis": "नैदानिक मार्ग",
        "status": "स्थिति: चिकित्सीय मूल्यांकन के लिए सुरक्षित प्रमाणित।",
    },
}


class ComplianceAgent:
    """Screen for PII/legal risk, then compose a localized clinical report."""

    def __init__(self) -> None:
        try:
            self._llm: GroqReasoningClient | None = GroqReasoningClient()
        except LLMReasoningError as exc:
            print(
                "[AGENT] Compliance: LLM unavailable, using localized "
                f"rule-based fallback ({exc})"
            )
            self._llm = None

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """Audit raw input, then compile a safe localized report."""

        print(
            "[AGENT] Compliance Officer running deterministic "
            "PII/legal-risk scan..."
        )

        redaction = redact_pii(state.raw_symptoms)
        profile, _ = resolve_language_profile(state.detected_language_code)

        if redaction.pii_detected or redaction.legal_risk_detected:
            status = f"FAILED: {'; '.join(redaction.reasons)}"

            print(
                f"[AGENT] Compliance BLOCKED - {status}. "
                "No patient content was sent to any LLM for this case."
            )

            token_log: Dict[str, Any] = {
                "node": "compliance_agent_pii_scan",
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
            }

            return {
                "compliance_status": status,
                "final_clinical_report": get_halt_message(
                    profile.assemblyai_code
                ),
                "current_step": "COMPLIANCE_AUDIT_COMPLETE",
                "token_usage_log": state.token_usage_log + [token_log],
            }

        if self._llm is not None:
            try:
                return await self._process_with_llm(
                    state,
                    redaction.redacted_text,
                    profile,
                )
            except LLMReasoningError as exc:
                print(
                    "[AGENT] Compliance LLM call failed, "
                    f"falling back to localized rules: {exc}"
                )

        return self._process_with_rules(state, profile)

    async def _process_with_llm(
        self,
        state: SharedState,
        redacted_text: str,
        profile: Any,
    ) -> Dict[str, Any]:

        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            language_name=profile.display_name,
            language_code=profile.assemblyai_code,
        )

        user_prompt = (
            f"TARGET LANGUAGE: {profile.display_name}\n"
            f"TARGET LANGUAGE CODE: {profile.assemblyai_code}\n"
            "IMPORTANT: The patient-facing report must be entirely in "
            f"{profile.display_name}. Do not answer in English.\n\n"
            f"Patient tracker ID: {state.patient_id}\n"
            f"Redacted patient statement: {redacted_text}\n"
            f"Extracted symptoms: "
            f"{', '.join(state.extracted_symptoms) or 'None'}\n"
            f"Diagnostic pathway: "
            f"{state.initial_diagnosis or 'Not yet determined'}"
        )

        parsed = await self._llm.complete_json(
            system_prompt,
            user_prompt,
        )

        report = str(
            parsed.get("patient_facing_report") or ""
        ).strip()

        if not report:
            raise LLMReasoningError(
                "LLM returned an empty patient_facing_report."
            )

        token_log = build_token_log(
            "compliance_agent",
            parsed.get("_usage", {}),
        )

        return {
            "compliance_status": "PASSED",
            "final_clinical_report": report,
            "current_step": "COMPLIANCE_AUDIT_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }

    def _process_with_rules(
        self,
        state: SharedState,
        profile: Any,
    ) -> Dict[str, Any]:
        """Create a deterministic fallback report in the detected language."""

        language_code = profile.assemblyai_code

        labels = _LOCALIZED_FALLBACKS.get(
            language_code,
            _LOCALIZED_FALLBACKS["en"],
        )

        symptoms = ", ".join(state.extracted_symptoms) or "None"
        diagnosis = state.initial_diagnosis or "Not yet determined"

        compiled_report = (
            f"{labels['title']}\n"
            f"=====================\n"
            f"{labels['tracker']}: {state.patient_id}\n"
            f"{labels['symptoms']}: {symptoms}\n"
            f"{labels['diagnosis']}: {diagnosis}\n"
            f"{labels['status']}"
        )

        token_log: Dict[str, Any] = {
            "node": "compliance_agent_localized_fallback",
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
