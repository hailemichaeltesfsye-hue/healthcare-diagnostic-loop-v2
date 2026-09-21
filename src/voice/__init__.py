"""Multilingual voice interaction layer for the diagnostic loop.

This package wraps two external services behind small, testable classes so
that they can be dropped into the LangGraph node execution lifecycle without
leaking API-specific details into the orchestration or agent layers:

- ``transcription_service``: AssemblyAI speech-to-text with automatic
  spoken-language detection.
- ``synthesis_service``: gTTS speech synthesis that renders the final
  clinical report back into the patient's detected language.
- ``nodes``: async LangGraph node adapters (``voice_input_node`` /
  ``voice_output_node``) that bind the two services to ``SharedState``.
"""

from src.voice.language_support import SUPPORTED_CLINICAL_LANGUAGES
from src.voice.nodes import voice_input_node, voice_output_node
from src.voice.synthesis_service import ClinicalReportSynthesizer
from src.voice.transcription_service import ClinicalAudioTranscriber

__all__ = [
    "SUPPORTED_CLINICAL_LANGUAGES",
    "ClinicalAudioTranscriber",
    "ClinicalReportSynthesizer",
    "voice_input_node",
    "voice_output_node",
]
