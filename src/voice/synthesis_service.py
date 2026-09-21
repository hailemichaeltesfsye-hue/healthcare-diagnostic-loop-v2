"""gTTS-backed speech synthesis for the final, patient-facing clinical report.

Converts the loop's compiled report text back into the patient's detected
native language as an MP3 file, with an optional (best-effort) local
autoplay step for interactive/demo use.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from src.voice.language_support import resolve_language_profile

try:
    from gtts import gTTS
    from gtts.tts import gTTSError
except ImportError as exc:  # pragma: no cover - surfaced at call time instead
    gTTS = None
    gTTSError = Exception
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class SynthesisServiceError(RuntimeError):
    """Raised for any recoverable failure in the speech synthesis pipeline."""


@dataclass
class SynthesisResult:
    """Structured payload describing the generated audio artifact."""

    audio_file_path: str
    spoken_language_code: str
    language_is_clinically_supported: bool
    playback_attempted: bool
    playback_succeeded: bool


class ClinicalReportSynthesizer:
    """Renders clinical report text to speech in the patient's own language.

    Parameters
    ----------
    output_dir:
        Directory MP3 files are written to. Created if missing.
    auto_play:
        When True, attempts to play the generated MP3 through the local
        audio device immediately after synthesis. This is best-effort: it is
        skipped silently (not treated as an error) in headless/server
        environments with no audio output, since the report is still
        available on disk either way.
    """

    def __init__(self, output_dir: str = "voice_output", auto_play: bool = True) -> None:
        if gTTS is None:
            raise SynthesisServiceError(
                "The 'gTTS' package is not installed. Run "
                "`uv pip install gTTS` (or `pip install gTTS`) and retry."
            ) from _IMPORT_ERROR

        self._output_dir = Path(output_dir).expanduser()
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._auto_play = auto_play

    def _synthesize_sync(
        self, report_text: str, detected_language_code: str | None, file_stem: str
    ) -> SynthesisResult:
        """Blocking synthesis (+ optional playback) call for a worker thread."""
        text = (report_text or "").strip()
        if not text:
            raise SynthesisServiceError(
                "Cannot synthesize speech from an empty clinical report."
            )

        profile, is_supported = resolve_language_profile(detected_language_code)

        output_path = self._output_dir / f"{file_stem}.mp3"
        try:
            speech = gTTS(text=text, lang=profile.gtts_code, lang_check=True)
            speech.save(str(output_path))
        except gTTSError as exc:
            raise SynthesisServiceError(
                f"gTTS failed to synthesize speech in "
                f"'{profile.display_name}' ({profile.gtts_code}): {exc}"
            ) from exc
        except (ValueError, OSError) as exc:
            raise SynthesisServiceError(
                f"Could not write synthesized audio to '{output_path}': {exc}"
            ) from exc

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
        )

    @staticmethod
    def _try_play(audio_path: Path) -> bool:
        """Best-effort local playback; never raises, only reports success."""
        try:
            from playsound import playsound  # Optional dependency.

            playsound(str(audio_path))
            return True
        except ImportError:
            print(
                "[VOICE] Skipping autoplay: install the optional 'playsound' "
                f"package to hear reports out loud. Report saved to {audio_path}."
            )
        except Exception as exc:  # Playback devices fail in many undocumented ways.
            print(
                f"[VOICE] Autoplay failed ({exc}); report saved to {audio_path} "
                "for manual playback."
            )
        return False

    async def synthesize(
        self,
        report_text: str,
        detected_language_code: str | None,
        file_stem: str | None = None,
    ) -> SynthesisResult:
        """Synthesize ``report_text`` in the patient's language without blocking.

        ``file_stem`` lets callers pin the output filename (e.g. to the
        patient tracker ID); a random UUID is used otherwise so concurrent
        graph runs never collide on disk.
        """
        stem = file_stem or f"clinical_report_{uuid.uuid4().hex[:12]}"
        try:
            return await asyncio.to_thread(
                self._synthesize_sync, report_text, detected_language_code, stem
            )
        except SynthesisServiceError:
            raise
        except Exception as exc:  # Defensive: never let a raw error escape.
            raise SynthesisServiceError(f"Unexpected synthesis failure: {exc}") from exc
