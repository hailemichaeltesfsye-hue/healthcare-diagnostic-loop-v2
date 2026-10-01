"""MedVoice AI: Real-Time Interactive Healthcare Voice Agent.

Orchestrates the entire voice lifecycle:
1. AssemblyAI Speech-to-Text with language auto-detection or profile locking.
2. Clinical Emergency & Red-Flag screening layer (immediate critical escalation).
3. PII/PHI redaction to maintain HIPAA/patient privacy before LLM reasoning.
4. Semantic Retrieval / RAG from ChromaDB ClinicalVectorStore.
5. Dynamic conversational reasoning with focused clinical follow-ups.
6. Structured Medical Summary generation for human clinician handoff.
7. Multilingual Speech Synthesis via hardened gTTS + browser fallback.
8. Medical disclaimer enforcement (AI assistant, not a physician).
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.compliance.pii_redaction import redact_pii
from src.db.vector_store import ClinicalVectorStore
from src.llm.groq_client import GroqReasoningClient, LLMReasoningError, build_token_log
from src.safety.emergency_detector import EmergencyDetector, RiskLevel, TriageAssessment
from src.voice.language_support import (
    DEFAULT_LANGUAGE_CODE,
    LanguageProfile,
    get_language_profile,
    resolve_language_profile,
)
from src.voice.synthesis_service import ClinicalReportSynthesizer, SynthesisResult
from src.voice.transcription_service import (
    ClinicalAudioTranscriber,
    TranscriptionResult,
    TranscriptionServiceError,
)


@dataclass
class ConversationTurn:
    """One back-and-forth exchange in a patient session."""

    turn_id: str
    timestamp: float
    speaker: str  # "patient" or "assistant"
    text: str
    audio_path: Optional[str] = None
    language_code: str = "en"
    risk_level: str = "ROUTINE"
    is_emergency: bool = False
    tokens_used: int = 0


@dataclass
class StructuredMedicalSummary:
    """Clinician-ready structured record compiled from the conversation."""

    patient_id: str
    chief_complaint: str
    extracted_symptoms: List[str] = field(default_factory=list)
    duration_onset: str = "Not specified"
    severity_character: str = "Not specified"
    triage_risk_level: str = "ROUTINE"  # ROUTINE | URGENT | EMERGENCY
    emergency_flags: List[str] = field(default_factory=list)
    clinical_evidence: str = ""
    recommended_next_steps: str = ""
    ai_disclaimer: str = ""
    language: str = "English"


@dataclass
class VoiceAgentResponse:
    """Complete output payload from a voice agent turn."""

    transcript: str
    assistant_response: str
    audio_file_path: Optional[str]
    detected_language_code: str
    language_display_name: str
    triage: TriageAssessment
    medical_summary: StructuredMedicalSummary
    suggested_follow_up: str = ""
    execution_time_seconds: float = 0.0


_VOICE_AGENT_SYSTEM_PROMPT = """You are "MedVoice AI", an empathetic, highly competent, safe AI healthcare voice assistant.
Your job is to engage with patients who describe symptoms out loud, gather essential clinical details through intelligent follow-up questions, and provide safe, supportive next-step guidance.

CRITICAL HEALTHCARE SAFETY RULES:
1. You are an AI assistant, NOT a physician. Never state or imply that you are a medical doctor.
2. DO NOT provide a definitive diagnosis (use phrases like "Possible causes could include..." or "Symptoms like this often relate to...").
3. DO NOT prescribe medications or suggest specific drug dosages.
4. If an emergency or red-flag is present, prioritize patient safety above all: advise immediate emergency services (911/112/local ER).
5. Always ask ONE focused, natural follow-up question per turn if important context is missing (duration, severity, exact location).
6. Always communicate in the patient's TARGET LANGUAGE: {language_name} ({language_code}).
7. Output your response as a valid JSON object with the following schema:
{{
    "conversational_response": "The natural speech to be spoken back to the patient in {language_name}.",
    "focused_follow_up": "A concise follow-up question in {language_name} asking about duration, severity, or onset.",
    "extracted_symptoms": ["symptom1", "symptom2"],
    "duration_onset": "Duration if mentioned, else 'Not specified'",
    "severity_character": "Severity (mild/moderate/severe) if mentioned, else 'Not specified'",
    "clinical_pathway": "Brief differential/educational pathway for clinician review",
    "recommended_next_steps": "Safe guidance on what to do next (home care, clinic appointment, urgent care, or emergency)"
}}
"""


class HealthcareVoiceAgent:
    """Conversational Healthcare Voice Agent integrating AssemblyAI, safety triage, RAG, and multilingual TTS."""

    def __init__(
        self,
        output_dir: str = "voice_output",
        vector_store: Optional[ClinicalVectorStore] = None,
    ) -> None:
        self.output_dir = output_dir
        self.transcriber: Optional[ClinicalAudioTranscriber] = None
        self.synthesizer = ClinicalReportSynthesizer(output_dir=output_dir, auto_play=False)
        self.safety_detector = EmergencyDetector()
        self.vector_store = vector_store or ClinicalVectorStore()

        try:
            self.llm: Optional[GroqReasoningClient] = GroqReasoningClient()
        except LLMReasoningError as exc:
            print(f"[VOICE_AGENT] LLM unavailable; running rule-based clinical fallback: {exc}")
            self.llm = None

    def _get_transcriber(self) -> ClinicalAudioTranscriber:
        if self.transcriber is None:
            self.transcriber = ClinicalAudioTranscriber()
        return self.transcriber

    async def process_voice_turn(
        self,
        audio_file_path: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        text_input: Optional[str] = None,
        language_preference: Optional[str] = "en",
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        patient_id: str = "PT-DEMO",
    ) -> VoiceAgentResponse:
        """Process one voice turn end-to-end with AssemblyAI, safety triage, and speech output."""
        start_time = time.time()
        detected_lang = language_preference or "en"
        confidence: Optional[float] = None
        transcript_text = ""

        # Step 1: AssemblyAI Speech-to-Text (if audio input provided)
        if audio_bytes is not None or audio_file_path is not None:
            transcriber = self._get_transcriber()
            try:
                if audio_bytes:
                    trans_result = await transcriber.transcribe_bytes(
                        audio_bytes=audio_bytes,
                        language_code=language_preference if language_preference != "auto" else None,
                    )
                else:
                    trans_result = await transcriber.transcribe(
                        audio_file_path=str(audio_file_path),
                        language_code=language_preference if language_preference != "auto" else None,
                    )
                transcript_text = trans_result.transcript_text
                detected_lang = trans_result.detected_language_code or language_preference or "en"
                confidence = trans_result.language_confidence
            except TranscriptionServiceError as exc:
                print(f"[VOICE_AGENT] AssemblyAI error: {exc}. Falling back to text if provided.")
                if not text_input:
                    raise

        if not transcript_text and text_input:
            transcript_text = text_input.strip()

        profile, _ = resolve_language_profile(detected_lang)

        # Step 2: Redact PII to protect patient privacy before any further processing
        redaction = redact_pii(transcript_text)
        safe_transcript = redaction.redacted_text

        # Step 3: Clinical Safety & Emergency Red-Flag Screening
        triage = self.safety_detector.evaluate(safe_transcript, profile.language_code)

        # Step 4: RAG Semantic Context Retrieval from ClinicalVectorStore
        retrieved_context = ""
        try:
            similar_cases = self.vector_store.search_similar_cases(safe_transcript, max_results=2)
            if similar_cases:
                retrieved_context = "\n".join(f"- {case}" for case in similar_cases)
        except Exception as exc:
            print(f"[VOICE_AGENT] RAG retrieval notice: {exc}")

        # Step 5: Healthcare Reasoning & Follow-up Generation
        if triage.is_emergency:
            # Emergency flow: immediate urgent escalation, skip delaying questions
            assistant_text = (
                f"{profile.emergency_warning}\n\n"
                f"{triage.immediate_guidance}\n\n"
                f"{profile.disclaimer}"
            )
            follow_up = "Please seek immediate emergency medical care now."
            extracted_symptoms = [f"EMERGENCY: {flag}" for flag in triage.matched_flags] or ["Critical Red-Flag"]
            medical_summary = StructuredMedicalSummary(
                patient_id=patient_id,
                chief_complaint=safe_transcript,
                extracted_symptoms=extracted_symptoms,
                duration_onset="Acute emergency presentation",
                severity_character="Severe / Critical Red-Flag",
                triage_risk_level=RiskLevel.EMERGENCY.value,
                emergency_flags=triage.matched_flags,
                clinical_evidence=retrieved_context or "Clinical emergency protocol activated.",
                recommended_next_steps="Call 911 / emergency services or go to nearest Emergency Department immediately.",
                ai_disclaimer=profile.disclaimer,
                language=profile.display_name,
            )
        else:
            # Standard conversational healthcare flow
            parsed_reasoning = await self._generate_clinical_response(
                safe_transcript=safe_transcript,
                profile=profile,
                retrieved_context=retrieved_context,
                conversation_history=conversation_history,
                triage=triage,
            )

            assistant_text = parsed_reasoning.get("conversational_response", "")
            follow_up = parsed_reasoning.get("focused_follow_up", "")
            symptoms = parsed_reasoning.get("extracted_symptoms", [])
            duration = parsed_reasoning.get("duration_onset", "Not specified")
            severity = parsed_reasoning.get("severity_character", "Not specified")
            next_steps = parsed_reasoning.get("recommended_next_steps", "")

            # Ensure AI disclaimer is appended
            if profile.disclaimer not in assistant_text:
                assistant_text = f"{assistant_text}\n\n{profile.disclaimer}"

            medical_summary = StructuredMedicalSummary(
                patient_id=patient_id,
                chief_complaint=safe_transcript,
                extracted_symptoms=symptoms if isinstance(symptoms, list) else [str(symptoms)],
                duration_onset=duration,
                severity_character=severity,
                triage_risk_level=triage.risk_level.value,
                emergency_flags=triage.matched_flags,
                clinical_evidence=retrieved_context or "Standard clinical consultation.",
                recommended_next_steps=next_steps or "Consult your primary healthcare provider for persistent symptoms.",
                ai_disclaimer=profile.disclaimer,
                language=profile.display_name,
            )

        # Step 6: Multilingual Speech Synthesis via hardened gTTS
        synth_result: SynthesisResult = await self.synthesizer.synthesize(
            report_text=assistant_text,
            detected_language_code=profile.assemblyai_code,
            file_stem=f"agent_turn_{uuid.uuid4().hex[:8]}",
        )

        elapsed = round(time.time() - start_time, 2)

        return VoiceAgentResponse(
            transcript=transcript_text,
            assistant_response=assistant_text,
            audio_file_path=synth_result.audio_file_path if synth_result.is_successful else None,
            detected_language_code=profile.assemblyai_code,
            language_display_name=f"{profile.flag_emoji} {profile.display_name}",
            triage=triage,
            medical_summary=medical_summary,
            suggested_follow_up=follow_up,
            execution_time_seconds=elapsed,
        )

    async def _generate_clinical_response(
        self,
        safe_transcript: str,
        profile: LanguageProfile,
        retrieved_context: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        triage: TriageAssessment,
    ) -> Dict[str, Any]:
        """Generate structured reasoning using Groq LLM or deterministic localized fallback."""
        if self.llm is None:
            return self._fallback_clinical_response(safe_transcript, profile, triage)

        sys_prompt = _VOICE_AGENT_SYSTEM_PROMPT.format(
            language_name=profile.display_name,
            language_code=profile.assemblyai_code,
        )

        history_snippets = ""
        if conversation_history:
            turns = []
            for t in conversation_history[-4:]:  # last 4 turns
                speaker = t.get("speaker", "user")
                text = t.get("text", "")
                turns.append(f"{speaker.upper()}: {text}")
            history_snippets = "\n".join(turns)

        user_prompt = (
            f"TARGET LANGUAGE: {profile.display_name} ({profile.native_name})\n"
            f"CLINICAL RISK LEVEL: {triage.risk_level.value}\n"
            f"SIMILAR CLINICAL CASES (RAG):\n{retrieved_context or 'None found'}\n\n"
            f"PRIOR CONVERSATION TURNS:\n{history_snippets or 'Start of conversation'}\n\n"
            f"PATIENT CURRENT SPOKEN INPUT:\n\"{safe_transcript}\"\n\n"
            f"Remember: Respond entirely in {profile.display_name}. Keep tone empathetic, ask one focused follow-up question, "
            f"do not make definitive diagnoses, and guide safely on next steps."
        )

        try:
            parsed = await self.llm.complete_json(sys_prompt, user_prompt)
            if not parsed.get("conversational_response"):
                raise LLMReasoningError("Empty conversational_response from LLM")
            return parsed
        except Exception as exc:
            print(f"[VOICE_AGENT] LLM reasoning failure: {exc}. Using deterministic fallback.")
            return self._fallback_clinical_response(safe_transcript, profile, triage)

    def _fallback_clinical_response(
        self,
        transcript: str,
        profile: LanguageProfile,
        triage: TriageAssessment,
    ) -> Dict[str, Any]:
        """Deterministic localized response when LLM is unavailable."""
        # Simple localized templates
        templates = {
            "en": {
                "resp": (
                    f"Thank you for sharing your symptoms regarding '{transcript}'. "
                    "I want to make sure you get the right care. "
                    "Could you share how long you have experienced this, and whether the discomfort is mild, moderate, or severe?"
                ),
                "follow_up": "How long have you had these symptoms, and how severe are they?",
                "steps": "Monitor your symptoms closely. If they worsen or persist, schedule a visit with your primary healthcare clinician.",
            },
            "am": {
                "resp": (
                    f"የገለጹትን ምልክት ተረድቻለሁ፦ '{transcript}'። ትክክለኛውን ድጋፍ እንድታገኙ እፈልጋለሁ። "
                    "ይህ ስሜት ከጀመረዎት ምን ያህል ጊዜ ሆነዎት? ሕመሙስ መጠነኛ ነው ወይስ በጣም ከባድ?"
                ),
                "follow_up": "ይህ ስሜት ከጀመረዎት ምን ያህል ጊዜ ሆነዎት?",
                "steps": "ምልክቶቹን በጥንቃቄ ይከታተሉ። ሕመሙ ከቀጠለ ወይም ከከበደ ወደ ጤና ተቋም በመሄድ ከሐኪም ጋር ይማከሩ።",
            },
            "ar": {
                "resp": (
                    f"شكراً لمشاركة الأعراض الخاصة بك: '{transcript}'. "
                    "أود أن أساعدك في الحصول على التوجيه الصحيح. "
                    "منذ متى تشعر بهذه الأعراض، وهل الألم خفيف أم متوسط أم شديد؟"
                ),
                "follow_up": "منذ متى بدأت هذه الأعراض وما مدى شدتها؟",
                "steps": "راقب الأعراض بدقة. إذا استمرت أو زادت حدتها يرجى حجز موعد مع طبيبك العام.",
            },
            "zh": {
                "resp": (
                    f"已收到您描述的症状：'{transcript}'。为了提供更准确的分诊建议，"
                    "请问这些症状已经持续了多长时间？感觉是轻微、中度还是剧烈不适？"
                ),
                "follow_up": "这些症状持续了多久？严重程度如何？",
                "steps": "请注意休息并持续监测体温及症状变化。若无好转或持续加重，请及时前往医院门诊就医。",
            },
            "fr": {
                "resp": (
                    f"J'ai bien noté vos symptômes : '{transcript}'. "
                    "Pour mieux vous orienter, depuis combien de temps ressentez-vous cela, "
                    "et l'inconfort est-il léger, modéré ou intense ?"
                ),
                "follow_up": "Depuis quand avez-vous ces symptômes et quelle est leur intensité ?",
                "steps": "Surveillez attentivement l'évolution de vos symptômes. S'ils persistent, prenez rendez-vous avec votre médecin traitant.",
            },
            "hi": {
                "resp": (
                    f"आपके द्वारा बताए गए लक्षणों को समझ लिया गया है: '{transcript}'। "
                    "सही मार्गदर्शन के लिए, क्या आप बता सकते हैं कि यह समस्या कब से है और दर्द हल्का है, मध्यम या तेज?"
                ),
                "follow_up": "यह लक्षण कब से हैं और इनकी तीव्रता कितनी है?",
                "steps": "अपने लक्षणों पर ध्यान दें। यदि समस्या बनी रहती है या बढ़ती है, तो अपने पारिवारिक चिकित्सक से परामर्श लें।",
            },
        }

        lang_data = templates.get(profile.language_code, templates["en"])
        return {
            "conversational_response": lang_data["resp"],
            "focused_follow_up": lang_data["follow_up"],
            "extracted_symptoms": [transcript[:40]],
            "duration_onset": "Pending patient reply",
            "severity_character": "Pending patient reply",
            "clinical_pathway": "Conservative Symptom Evaluation",
            "recommended_next_steps": lang_data["steps"],
        }
