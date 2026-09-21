"""LangGraph node adapters binding the voice services to ``SharedState``.

These follow the exact pattern already used in ``src/graph/nodes.py``: an
async function that takes the current ``SharedState`` and returns a partial
dict of fields to merge, never mutating the caller's state object. This lets
the voice loop slot directly into ``compile_workflow`` alongside the existing
triage/researcher/diagnostic/compliance/hitl nodes.
"""

import os
from typing import Any, Dict

from src.graph.state import SharedState
from src.voice.synthesis_service import ClinicalReportSynthesizer, SynthesisServiceError
from src.voice.transcription_service import (
    ClinicalAudioTranscriber,
    TranscriptionServiceError,
)


def _auto_play_enabled() -> bool:
    """Read VOICE_AUTO_PLAY from the environment (default: on).

    Server-side ``playsound`` autoplay only makes sense for local/CLI use
    (``scripts/run_voice_loop.py``). A browser-based deployment (e.g. the
    Streamlit app) plays the MP3 client-side via ``st.audio(..., autoplay=
    True)`` instead, so set ``VOICE_AUTO_PLAY=false`` in that environment to
    avoid the server uselessly attempting to play audio on its own speakers.
    """
    return os.getenv("VOICE_AUTO_PLAY", "true").strip().lower() not in ("0", "false", "no")

# Instantiated lazily so importing this module never requires API keys to be
# configured (e.g. text-only Streamlit sessions with no audio input/output).
_transcriber: ClinicalAudioTranscriber | None = None
_synthesizer: ClinicalReportSynthesizer | None = None


def _get_transcriber() -> ClinicalAudioTranscriber:
    global _transcriber
    if _transcriber is None:
        _transcriber = ClinicalAudioTranscriber()
    return _transcriber


def _get_synthesizer() -> ClinicalReportSynthesizer:
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = ClinicalReportSynthesizer(auto_play=_auto_play_enabled())
    return _synthesizer


def _cleanup_audio_file(path: str) -> None:
    """Best-effort deletion of raw patient audio once it's no longer needed.

    Raw audio is PHI. Set KEEP_VOICE_AUDIO_ARTIFACTS=true to keep files
    around for local debugging (never recommended in a real deployment).
    """
    if os.getenv("KEEP_VOICE_AUDIO_ARTIFACTS", "false").strip().lower() in ("1", "true", "yes"):
        return
    try:
        os.remove(path)
    except OSError as exc:
        print(f"[AGENT] Could not remove temporary audio file '{path}': {exc}")


async def voice_input_node(state: SharedState) -> Dict[str, Any]:
    """Transcribe ``state.input_audio_path`` and detect its spoken language.

    Runs before ``triage``. When no audio path is set, this is a no-op that
    preserves full backward compatibility with the existing text-only
    Streamlit intake form — ``raw_symptoms`` is simply left as-is.

    The raw audio file is deleted once transcription finishes (success or
    failure): it is PHI and there is no reason to retain it once a transcript
    exists. Set KEEP_VOICE_AUDIO_ARTIFACTS=true to disable this for local
    debugging.
    """
    if not state.input_audio_path:
        return {"current_step": "VOICE_INPUT_SKIPPED_NO_AUDIO"}

    audio_path = state.input_audio_path
    print(f"[AGENT] Voice input transcribing '{audio_path}'...")
    try:
        transcriber = _get_transcriber()
        result = await transcriber.transcribe(audio_path)
    except TranscriptionServiceError as exc:
        print(f"[AGENT] Voice input failed: {exc}")
        _cleanup_audio_file(audio_path)
        return {
            "current_step": "VOICE_INPUT_FAILED",
            "voice_input_error": str(exc),
        }

    _cleanup_audio_file(audio_path)

    if not result.language_is_clinically_supported:
        print(
            f"[AGENT] Detected language '{result.detected_language_code}' is "
            "outside the six clinically-supported languages; defaulting "
            "downstream voice output to English."
        )

    # Callers (e.g. the Streamlit intake form) may pre-fill raw_symptoms with
    # structured patient metadata ("Patient Jordan Morgan, age 48... Symptoms:")
    # before attaching audio. Append rather than overwrite so that context
    # survives the voice round-trip instead of being discarded.
    combined_symptoms = (
        f"{state.raw_symptoms.strip()} {result.transcript_text}".strip()
        if state.raw_symptoms.strip()
        else result.transcript_text
    )

    token_log: Dict[str, Any] = {
        "node": "voice_input_node",
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost": 0.0,
    }
    return {
        "raw_symptoms": combined_symptoms,
        "detected_language_code": result.detected_language_code,
        "language_confidence": result.language_confidence,
        "current_step": "VOICE_INPUT_COMPLETE",
        "token_usage_log": state.token_usage_log + [token_log],
    }


async def voice_output_node(state: SharedState) -> Dict[str, Any]:
    """Speak ``state.final_clinical_report`` back in the patient's language.

    Runs after ``final_compile``. Always synthesizes whatever the final
    report currently says — including "pending HITL approval" or
    "compliance blocked" messages — so the patient reliably hears the
    current status of their case in their own language, not just a
    fully-approved report.
    """
    print(
        f"[AGENT] Voice output synthesizing report in "
        f"'{state.detected_language_code}'..."
    )
    try:
        synthesizer = _get_synthesizer()
        result = await synthesizer.synthesize(
            report_text=state.final_clinical_report,
            detected_language_code=state.detected_language_code,
            file_stem=state.patient_id or None,
        )
    except SynthesisServiceError as exc:
        print(f"[AGENT] Voice output failed: {exc}")
        return {
            "current_step": "VOICE_OUTPUT_FAILED",
            "voice_output_error": str(exc),
        }

    return {
        "output_audio_path": result.audio_file_path,
        "current_step": "VOICE_OUTPUT_COMPLETE",
    }
