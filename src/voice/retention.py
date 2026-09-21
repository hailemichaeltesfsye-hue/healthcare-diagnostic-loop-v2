"""Retention helpers for synthesized voice-output artifacts.

Spoken clinical reports (the MP3s in ``voice_output/``) are PHI. Unlike the
raw input audio (deleted immediately after transcription - see
``src/voice/nodes.py``), these need to persist at least long enough for the
patient/practitioner to actually play them back, so they can't be deleted
the instant they're created. This module gives operators a simple way to
purge anything past a retention window instead of letting them accumulate
indefinitely; see ``scripts/purge_voice_outputs.py`` for a schedulable CLI.
"""

from __future__ import annotations

import time
from pathlib import Path


def purge_old_audio_files(directory: str, max_age_seconds: float) -> int:
    """Delete ``*.mp3`` files under ``directory`` older than ``max_age_seconds``.

    Returns the number of files removed. Missing directories are treated as
    "nothing to purge" rather than an error, since a fresh deployment may not
    have created the output directory yet.
    """
    root = Path(directory)
    if not root.exists():
        return 0

    cutoff = time.time() - max_age_seconds
    removed = 0
    for path in root.glob("*.mp3"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError as exc:
            print(f"[RETENTION] Could not remove '{path}': {exc}")
    return removed
