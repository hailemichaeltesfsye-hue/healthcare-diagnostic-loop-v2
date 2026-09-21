"""Delete synthesized voice-report MP3s older than a retention window.

Spoken clinical reports are PHI and should not accumulate on disk
indefinitely. Schedule this via cron (Linux/Mac) or Task Scheduler
(Windows) - e.g. nightly - rather than relying on someone to run it by hand.

Usage:
    uv run python scripts/purge_voice_outputs.py --hours 24
    uv run python scripts/purge_voice_outputs.py --dir voice_output --hours 1
"""

import argparse

from src.voice.retention import purge_old_audio_files


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the retention sweep."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default="voice_output",
        help="Directory of synthesized MP3s to sweep (default: %(default)s).",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=24.0,
        help="Delete files older than this many hours (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    removed = purge_old_audio_files(args.dir, args.hours * 3600)
    print(f"Removed {removed} audio file(s) older than {args.hours} hour(s) from '{args.dir}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
