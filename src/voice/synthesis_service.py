"""Multilingual speech synthesis service with robust text sanitization and multi-TLD fallback.

Converts healthcare responses and clinical reports into natural spoken audio in the
patient's detected native language. Solves network connectivity and provider limitations
by using pre-validated language profiles (lang_check=False), markdown sanitization,
multi-TLD backoff (com, co.uk, ca), and graceful text fallback.
"""

from __future__ import annotations

import asyncio
import os
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from src.voice.language_support import resolve_language_profile

try:
    from gtts import gTTS
    from gtts.tts import gTTSError
except ImportError as exc:  # pragma: no cover
    gTTS = None
    gTTSError = Exception
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class SynthesisServiceError(RuntimeError):
    """Raised for any critical failure in the speech synthesis pipeline."""


@dataclass
class SynthesisResult:
    """Structured payload describing the generated audio artifact."""

    audio_file_path: str
    spoken_language_code: str
    language_is_clinically_supported: bool
    playback_attempted: bool
    playback_succeeded: bool
    is_successful: bool = True
    error_message: str | None = None


def sanitize_text_for_speech(text: str) -> str:
    """Strip markdown formatting, symbols, and formatting that disrupt TTS tokenization."""
    if not text:
        return ""

    cleaned = text.strip()
    # Strip code blocks
    cleaned = re.sub(r"```[\s\S]*?```", "", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Strip markdown headers, bold, italics, strikethrough
    cleaned = re.sub(r"^\s*#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"~~([^~]+)~~", r"\1", cleaned)
    # Strip URLs and markdown links
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Strip emojis and special decorative divider lines
    cleaned = re.sub(r"^[\s\-=*_]{3,}\s*$", "", cleaned, flags=re.MULTILINE)
    # Strip bullet characters
    cleaned = re.sub(r"^\s*[-*•]\s+", "", cleaned, flags=re.MULTILINE)
    # Remove excessive blank lines
    cleaned = re.sub(r"\n{2,}", ". ", cleaned)
    cleaned = cleaned.replace("\n", " ").strip()
    return cleaned


class ClinicalReportSynthesizer:
    """Renders clinical narrative and healthcare responses to speech in the patient's language.

    Parameters
    ----------
    output_dir:
        Directory MP3 files are written to. Created if missing.
    auto_play:
        When True, attempts local audio playback through the system sound device.
    """

    def __init__(self, output_dir: str = "voice_output", auto_play: bool = True) -> None:
        if gTTS is None:
            raise SynthesisServiceError(
                "The 'gTTS' package is not installed. Run "
                "`pip install gTTS` and retry."
            ) from _IMPORT_ERROR

        self._output_dir = Path(output_dir).expanduser()
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._auto_play = auto_play

    def _synthesize_sync(
        self, report_text: str, detected_language_code: str | None, file_stem: str
    ) -> SynthesisResult:
        """Blocking synthesis with multi-TLD retry and robust sanitization."""
        raw_text = (report_text or "").strip()
        if not raw_text:
            raise SynthesisServiceError("Cannot synthesize speech from empty text.")

        speech_text = sanitize_text_for_speech(raw_text)
        if not speech_text:
            speech_text = raw_text

        profile, is_supported = resolve_language_profile(detected_language_code)
        output_path = self._output_dir / f"{file_stem}.mp3"

        # Multi-TLD retry loop to bypass transient connection failures & rate limits
        tlds_to_try = list(profile.tts_tlds) if profile.tts_tlds else ["com", "co.uk", "ca"]
        last_exception: Exception | None = None
        synthesis_succeeded = False

        for tld in tlds_to_try:
            try:
                # lang_check=False prevents the extra fragile HTTP call to translate.google.com
                # which was the primary root cause of "Failed to connect" errors!
                speech = gTTS(
                    text=speech_text,
                    lang=profile.gtts_code,
                    tld=tld,
                    lang_check=False,
                    slow=False,
                )
                speech.save(str(output_path))
                synthesis_succeeded = True
                break
            except Exception as exc:
                last_exception = exc
                time.sleep(0.3)  # brief backoff before trying alternate TLD

        if not synthesis_succeeded:
            error_msg = (
                f"gTTS failed across all fallback endpoints ({', '.join(tlds_to_try)}) "
                f"for '{profile.display_name}' ({profile.gtts_code}): {last_exception}"
            )
            print(f"[VOICE] Speech synthesis warning: {error_msg}. Falling back to visual text.")
            return SynthesisResult(
                audio_file_path="",
                spoken_language_code=profile.assemblyai_code,
                language_is_clinically_supported=is_supported,
                playback_attempted=False,
                playback_succeeded=False,
                is_successful=False,
                error_message=error_msg,
            )

        playback_attempted = False
        playback_succeeded = False
        if self._auto_play:
            playback_attempted = True
            playback_succeeded = self._try_play(output_path)

        return SynthesisResult(
            audio_file_path=str(output_path),
            spoken_language_code=profile.assemblyai_code,
            language_is_clinically_supported=is_supported,
            playback_attempted=playback_attempted,
            playback_succeeded=playback_succeeded,
            is_successful=True,
            error_message=None,
        )

    @staticmethod
    def _try_play(audio_path: Path) -> bool:
        """Best-effort local playback; never raises, only reports success."""
        try:
            from playsound import playsound

            playsound(str(audio_path))
            return True
        except ImportError:
            pass
        except Exception as exc:
            print(f"[VOICE] Autoplay notice ({exc}); audio saved to {audio_path}.")
        return False

    async def synthesize(
        self,
        report_text: str,
        detected_language_code: str | None,
        file_stem: str | None = None,
    ) -> SynthesisResult:
        """Synthesize ``report_text`` in the patient's language asynchronously."""
        stem = file_stem or f"voice_response_{uuid.uuid4().hex[:12]}"
        try:
            return await asyncio.to_thread(
                self._synthesize_sync, report_text, detected_language_code, stem
            )
        except SynthesisServiceError:
            raise
        except Exception as exc:
            return SynthesisResult(
                audio_file_path="",
                spoken_language_code=(detected_language_code or "en"),
                language_is_clinically_supported=False,
                playback_attempted=False,
                playback_succeeded=False,
                is_successful=False,
                error_message=f"Synthesis error: {exc}",
            )
