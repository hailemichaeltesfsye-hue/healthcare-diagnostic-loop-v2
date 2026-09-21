"""AssemblyAI-backed speech-to-text with automatic clinical language detection.

Wraps the AssemblyAI SDK so that the rest of the diagnostic loop only ever
deals with a plain, structured :class:`TranscriptionResult` — never with
SDK-specific objects, network exceptions, or polling details.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path

from src.voice.language_support import resolve_language_profile

try:
    import assemblyai as aai
except ImportError as exc:  # pragma: no cover - surfaced at call time instead
    aai = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class TranscriptionServiceError(RuntimeError):
    """Raised for any recoverable failure in the transcription pipeline."""


@dataclass
class TranscriptionResult:
    """Structured payload handed to the orchestration layer after STT."""

    transcript_text: str
    detected_language_code: str
    language_is_clinically_supported: bool
    language_confidence: float | None
    audio_duration_seconds: float | None


class ClinicalAudioTranscriber:
    """Transcribes patient-reported symptoms from audio with language auto-detection.

    Parameters
    ----------
    api_key:
        AssemblyAI API key. Falls back to the ``ASSEMBLYAI_API_KEY``
        environment variable when omitted.
    language_confidence_threshold:
        Minimum confidence AssemblyAI must reach for its detected language to
        be trusted before this service also cross-checks it against the six
        clinically-supported languages.
    """

    _MAX_AUDIO_BYTES = 100 * 1024 * 1024  # 100 MB safety ceiling.

    def __init__(
        self,
        api_key: str | None = None,
        language_confidence_threshold: float = 0.4,
    ) -> None:
        if aai is None:
            raise TranscriptionServiceError(
                "The 'assemblyai' package is not installed. Run "
                "`uv pip install assemblyai` (or `pip install assemblyai`) "
                "and retry."
            ) from _IMPORT_ERROR

        resolved_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not resolved_key:
            raise TranscriptionServiceError(
                "No AssemblyAI API key was provided. Set the "
                "ASSEMBLYAI_API_KEY environment variable or pass api_key= "
                "explicitly."
            )

        aai.settings.api_key = resolved_key
        self._language_confidence_threshold = language_confidence_threshold
        self._transcriber = aai.Transcriber()

    def _validate_audio_path(self, audio_file_path: str) -> Path:
        path = Path(audio_file_path).expanduser()
        if not path.exists():
            raise TranscriptionServiceError(f"Audio file not found: {path}")
        if not path.is_file():
            raise TranscriptionServiceError(f"Audio path is not a file: {path}")
        size = path.stat().st_size
        if size == 0:
            raise TranscriptionServiceError(f"Audio file is empty: {path}")
        if size > self._MAX_AUDIO_BYTES:
            raise TranscriptionServiceError(
                f"Audio file ({size / (1024 * 1024):.1f} MB) exceeds the "
                f"{self._MAX_AUDIO_BYTES / (1024 * 1024):.0f} MB safety ceiling."
            )
        return path

    def _transcribe_sync(self, audio_file_path: str) -> TranscriptionResult:
        """Blocking transcription call, intended to run in a worker thread."""
        path = self._validate_audio_path(audio_file_path)

        config = aai.TranscriptionConfig(
            language_detection=True,
            language_confidence_threshold=self._language_confidence_threshold,
        )

        try:
            transcript = self._transcriber.transcribe(str(path), config=config)
        except Exception as exc:  # AssemblyAI SDK raises a mix of exception types.
            raise TranscriptionServiceError(
                f"AssemblyAI request failed for '{path.name}': {exc}"
            ) from exc

        if transcript.status == aai.TranscriptStatus.error:
            raise TranscriptionServiceError(
                f"AssemblyAI returned a transcription error for '{path.name}': "
                f"{transcript.error}"
            )

        transcript_text = (transcript.text or "").strip()
        if not transcript_text:
            raise TranscriptionServiceError(
                f"AssemblyAI returned an empty transcript for '{path.name}'. "
                "The audio may be silent, corrupted, or too short."
            )

        detected_code = getattr(transcript, "language_code", None)
        confidence = getattr(transcript, "language_confidence", None)
        _, is_supported = resolve_language_profile(detected_code)

        return TranscriptionResult(
            transcript_text=transcript_text,
            detected_language_code=(detected_code or "en").lower(),
            language_is_clinically_supported=is_supported,
            language_confidence=confidence,
            audio_duration_seconds=getattr(transcript, "audio_duration", None),
        )

    async def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe ``audio_file_path`` without blocking the event loop.

        The AssemblyAI SDK's ``transcribe`` call is synchronous under the
        hood (it polls until the job completes), so it is offloaded to a
        worker thread to stay compatible with LangGraph's async node
        execution lifecycle.
        """
        try:
            return await asyncio.to_thread(self._transcribe_sync, audio_file_path)
        except TranscriptionServiceError:
            raise
        except Exception as exc:  # Defensive: never let a raw SDK error escape.
            raise TranscriptionServiceError(
                f"Unexpected transcription failure: {exc}"
            ) from exc
