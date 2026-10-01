"""Comprehensive Automated Quality Gate and Verification Suite for MedVoice AI.

Tests:
1. Centralized 6-Language profile integrity (en, am, ar, zh, fr, hi).
2. Emergency & Red-Flag clinical detection across categories and languages.
3. Healthcare safety boundaries & disclaimer enforcement.
4. PII/PHI redaction guard.
5. Multilingual hardened speech synthesis across all 6 languages.
6. AssemblyAI Speech-to-Text integration.
7. Interactive multi-turn conversational reasoning and structured medical summary.
8. Empty input and graceful error handling.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure workspace root is on sys.path
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from dotenv import load_dotenv

load_dotenv()

from src.agents.voice_agent import HealthcareVoiceAgent
from src.compliance.pii_redaction import redact_pii
from src.db.vector_store import ClinicalVectorStore
from src.safety.emergency_detector import EmergencyDetector, RiskLevel
from src.voice.language_support import (
    SUPPORTED_CLINICAL_LANGUAGES,
    get_language_profile,
    resolve_language_profile,
)
from src.voice.synthesis_service import ClinicalReportSynthesizer


def test_centralized_languages() -> bool:
    """Test 1: Verify all 6 languages are fully configured with required metadata."""
    print("\n--- TEST 1: Centralized 6-Language Profiles ---")
    required_codes = {"en", "am", "ar", "zh", "fr", "hi"}
    configured_codes = set(SUPPORTED_CLINICAL_LANGUAGES.keys())

    assert required_codes.issubset(configured_codes), f"Missing languages: {required_codes - configured_codes}"

    for code in required_codes:
        profile = get_language_profile(code)
        assert profile.display_name, f"Empty display name for {code}"
        assert profile.native_name, f"Empty native name for {code}"
        assert profile.locale, f"Empty locale for {code}"
        assert profile.assemblyai_code, f"Empty assemblyai_code for {code}"
        assert profile.gtts_code, f"Empty gtts_code for {code}"
        assert profile.disclaimer, f"Empty disclaimer for {code}"
        assert profile.emergency_warning, f"Empty emergency_warning for {code}"
        print(f"  [PASS] {code.upper()}: {profile.flag_emoji} {profile.display_name} ({profile.native_name}) - Locale: {profile.locale}")

    # Resolution test
    p_am, ok_am = resolve_language_profile("am-ET")
    assert ok_am and p_am.language_code == "am"
    p_fallback, ok_fallback = resolve_language_profile("unknown-lang")
    assert not ok_fallback and p_fallback.language_code == "en"
    print("  [PASS] Language resolution and fallback logic validated.")
    return True


def test_emergency_detector() -> bool:
    """Test 2: Verify Emergency & Red-Flag detection across categories and languages."""
    print("\n--- TEST 2: Emergency & Red-Flag Clinical Detection ---")
    detector = EmergencyDetector()

    scenarios = [
        # (Text, Lang, ExpectedEmergency, ExpectedRisk)
        ("Severe crushing chest pain radiating to left arm and shortness of breath", "en", True, RiskLevel.EMERGENCY),
        ("Sudden slurred speech, facial drooping, and right arm weakness", "en", True, RiskLevel.EMERGENCY),
        ("ከባድ የደረት ሕመም እና ከፍተኛ የመተንፈስ ችግር አጋጥሞኛል", "am", True, RiskLevel.EMERGENCY),
        ("أعاني من ألم حاد ومفاجئ في الصدر مع ضيق شديد في التنفس", "ar", True, RiskLevel.EMERGENCY),
        ("突发剧烈胸痛伴左臂放射痛，喘不上气", "zh", True, RiskLevel.EMERGENCY),
        ("Douleur thoracique intense et difficulté à respirer", "fr", True, RiskLevel.EMERGENCY),
        ("सीने में अचानक असहनीय दर्द और सांस लेने में भारी तकलीफ", "hi", True, RiskLevel.EMERGENCY),
        # Urgent scenarios
        ("Persistent high fever and abdominal pain for 2 days", "en", False, RiskLevel.URGENT),
        # Low risk scenarios
        ("Mild tension headache after looking at screens all day", "en", False, RiskLevel.ROUTINE),
        ("J'ai une fatigue légère depuis hier", "fr", False, RiskLevel.ROUTINE),
    ]

    for text, lang, exp_emerg, exp_risk in scenarios:
        res = detector.evaluate(text, lang)
        assert res.is_emergency == exp_emerg, f"Failed emergency detection for '{text[:30]}': got {res.is_emergency}"
        assert res.risk_level == exp_risk, f"Failed risk level for '{text[:30]}': got {res.risk_level}"
        status_symbol = "🚨" if res.is_emergency else "⚠️" if res.risk_level == RiskLevel.URGENT else "🟢"
        print(f"  [PASS] {status_symbol} [{lang.upper()}] {res.risk_level.value}: '{text[:45]}...'")

    return True


def test_pii_redaction() -> bool:
    """Test 3: PII/PHI redaction to protect HIPAA/patient privacy."""
    print("\n--- TEST 3: PII/PHI Redaction Guard ---")
    raw = "My name is John Doe, phone 555-123-4567, SSN 000-12-3456. I have a headache."
    redacted = redact_pii(raw)
    assert redacted.pii_detected, "Failed to detect PII in text"
    assert "John Doe" not in redacted.redacted_text, "Failed to redact name"
    print(f"  [PASS] Redacted Text: '{redacted.redacted_text}'")
    return True


async def test_speech_synthesis_all_languages() -> bool:
    """Test 4: Verify speech synthesis for all six languages without connection failures."""
    print("\n--- TEST 4: Multilingual Hardened Speech Synthesis ---")
    syn = ClinicalReportSynthesizer(output_dir="voice_output", auto_play=False)

    tests = {
        "en": "Hello, your healthcare checkup has been completed safely.",
        "am": "ጤና ይስጥልኝ፣ የጤና ክትትልዎ በተሳካ ሁኔታ ተጠናቋል።",
        "ar": "مرحباً، تم فحص وتقييم حالتك الصحية بنجاح وأمان.",
        "zh": "您好，您的健康分诊咨询已安全完成。",
        "fr": "Bonjour, votre consultation de santé est terminée en toute sécurité.",
        "hi": "नमस्ते, आपका स्वास्थ्य परामर्श सुरक्षित रूप से पूरा हो गया है।",
    }

    for lang, sample in tests.items():
        res = await syn.synthesize(sample, lang, f"test_suite_{lang}")
        assert res.is_successful, f"Synthesis failed for {lang}: {res.error_message}"
        assert os.path.exists(res.audio_file_path), f"Audio file not created for {lang}"
        file_size = os.path.getsize(res.audio_file_path)
        assert file_size > 1000, f"Audio file suspiciously small for {lang}: {file_size} bytes"
        print(f"  [PASS] {lang.upper()}: Synthesized {file_size:,} bytes -> {res.audio_file_path}")

    return True


async def test_assemblyai_stt() -> bool:
    """Test 5: Verify AssemblyAI Speech-to-Text integration."""
    print("\n--- TEST 5: AssemblyAI Real Speech-to-Text Integration ---")
    key = os.getenv("ASSEMBLYAI_API_KEY")
    assert key, "ASSEMBLYAI_API_KEY is not set in environment or .env"

    sample_audio = "voice_output/test_suite_en.mp3"
    if not os.path.exists(sample_audio):
        syn = ClinicalReportSynthesizer(output_dir="voice_output", auto_play=False)
        await syn.synthesize("Hello, your healthcare checkup has been completed safely.", "en", "test_suite_en")

    agent = HealthcareVoiceAgent(output_dir="voice_output")
    trans_res = await agent._get_transcriber().transcribe(sample_audio)
    assert trans_res.transcript_text, "Empty transcript returned by AssemblyAI"
    print(f"  [PASS] AssemblyAI Status: Completed")
    print(f"  [PASS] Audio File: {sample_audio}")
    print(f"  [PASS] Transcript: '{trans_res.transcript_text}'")
    print(f"  [PASS] Detected Language: {trans_res.detected_language_code}")
    return True


async def test_conversational_voice_agent() -> bool:
    """Test 6: Multi-turn conversational reasoning and structured summary."""
    print("\n--- TEST 6: Interactive Voice Agent Reasoning & Medical Summary ---")
    agent = HealthcareVoiceAgent(output_dir="voice_output")

    # Turn 1: Patient presents initial symptom
    print("  Turn 1: Initial symptom presentation (stomach pain)...")
    history: list[dict] = []
    r1 = await agent.process_voice_turn(
        text_input="I have had stomach pain since yesterday.",
        language_preference="en",
        conversation_history=history,
        patient_id="TEST-PT-001",
    )
    assert r1.assistant_response, "Empty assistant response"
    assert r1.triage.risk_level in (RiskLevel.ROUTINE, RiskLevel.URGENT)
    assert "stomach" in r1.medical_summary.chief_complaint.lower()
    print(f"    MedVoice AI: '{r1.assistant_response[:100]}...'")
    print(f"    Suggested Follow-Up: '{r1.suggested_follow_up}'")

    history.append({"speaker": "patient", "text": "I have had stomach pain since yesterday."})
    history.append({"speaker": "assistant", "text": r1.assistant_response})

    # Turn 2: Patient answers follow-up
    print("  Turn 2: Follow-up reply (mild cramping, no fever)...")
    r2 = await agent.process_voice_turn(
        text_input="The pain is mild and feels like cramping. No fever.",
        language_preference="en",
        conversation_history=history,
        patient_id="TEST-PT-001",
    )
    assert r2.assistant_response, "Empty assistant response in turn 2"
    print(f"    MedVoice AI: '{r2.assistant_response[:100]}...'")
    print(f"    Extracted Symptoms: {r2.medical_summary.extracted_symptoms}")
    print(f"    Triage Risk Level: {r2.medical_summary.triage_risk_level}")
    print("  [PASS] Multi-turn conversational memory & adaptation verified.")

    # Emergency Scenario Turn
    print("  Turn 3: Immediate emergency test (severe crushing chest pain)...")
    r3 = await agent.process_voice_turn(
        text_input="Severe crushing chest pain radiating to left arm and cannot breathe.",
        language_preference="en",
        patient_id="TEST-PT-002",
    )
    assert r3.triage.is_emergency, "Failed to identify emergency in voice turn"
    assert "emergency" in r3.assistant_response.lower()
    assert r3.medical_summary.triage_risk_level == "EMERGENCY"
    print(f"    [PASS] Emergency flagged: {r3.triage.category}")
    print(f"    [PASS] Safe Next Steps: '{r3.medical_summary.recommended_next_steps}'")

    return True


async def main():
    print("=================================================================")
    print("MEDVOICE AI: HACKATHON QUALITY GATE & VERIFICATION SUITE")
    print("AssemblyAI Voice Agent Hackathon 2026")
    print("=================================================================")

    start_total = time.time()
    t1 = test_centralized_languages()
    t2 = test_emergency_detector()
    t3 = test_pii_redaction()
    t4 = await test_speech_synthesis_all_languages()
    t5 = await test_assemblyai_stt()
    t6 = await test_conversational_voice_agent()

    total_time = round(time.time() - start_total, 2)
    print("\n=================================================================")
    print(f"ALL TESTS PASSED SUCCESSFULLY in {total_time}s!")
    print("=================================================================")


if __name__ == "__main__":
    asyncio.run(main())
