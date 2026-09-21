"""End-to-end CLI demo of the autonomous multilingual voice interaction loop.

Feeds a patient audio file into the full LangGraph pipeline (voice input ->
triage -> researcher -> diagnostic -> compliance -> HITL -> final compile ->
voice output) and reports where the generated MP3 landed.

Usage:
    uv run python scripts/run_voice_loop.py path/to/symptoms.wav
    uv run python scripts/run_voice_loop.py path/to/symptoms.wav --patient-id PT-1123 --auto-approve
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from src.graph.pipeline import compile_workflow
from src.graph.state import SharedState


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the voice-loop demo run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio_path", help="Path to a patient audio recording.")
    parser.add_argument(
        "--patient-id",
        default="PT-VOICE-DEMO",
        help="Patient tracker ID used to name the output MP3 (default: %(default)s).",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help=(
            "Skip the HITL pause and immediately re-run with hitl_approved=True, "
            "as a real UI would do after a practitioner clicks 'Approve'."
        ),
    )
    return parser.parse_args()


async def run(audio_path: str, patient_id: str, auto_approve: bool) -> int:
    """Execute the compiled graph once (and again after approval, if requested)."""
    load_dotenv()

    for required_var in ("ASSEMBLYAI_API_KEY", "GROQ_API_KEY"):
        if not os.getenv(required_var, "").strip():
            print(f"Warning: {required_var} is not set in the environment/.env file.")

    if not os.path.isfile(audio_path):
        print(f"Error: audio file not found: {audio_path}")
        return 1

    graph = compile_workflow()

    print(f"\n=== Run 1: transcribing '{audio_path}' and reaching the HITL checkpoint ===")
    initial_state = SharedState(patient_id=patient_id, input_audio_path=audio_path)
    result = await graph.ainvoke(initial_state)

    print(f"Detected language:     {result['detected_language_code']}")
    print(f"Language confidence:   {result.get('language_confidence')}")
    print(f"Transcribed symptoms:  {result['raw_symptoms']!r}")
    print(f"Current step:          {result['current_step']}")
    print(f"Report (pending):\n{result['final_clinical_report']}")
    if result.get("output_audio_path"):
        print(f"Spoken report (pending status): {result['output_audio_path']}")
    if result.get("voice_input_error"):
        print(f"Voice input error: {result['voice_input_error']}")
        return 1

    if not auto_approve:
        print(
            "\nPass --auto-approve to simulate practitioner sign-off and hear "
            "the final approved report synthesized as well."
        )
        return 0

    print("\n=== Run 2: practitioner approval, re-running to final compile ===")
    approved_state = SharedState(
        patient_id=patient_id,
        raw_symptoms=result["raw_symptoms"],
        extracted_symptoms=result["extracted_symptoms"],
        detected_language_code=result["detected_language_code"],
        hitl_approved=True,
    )
    final_result = await graph.ainvoke(approved_state)

    print(f"Current step:   {final_result['current_step']}")
    print(f"Final report:\n{final_result['final_clinical_report']}")
    if final_result.get("output_audio_path"):
        print(f"\nSpoken final report saved to: {final_result['output_audio_path']}")
    if final_result.get("voice_output_error"):
        print(f"Voice output error: {final_result['voice_output_error']}")
        return 1
    return 0


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    return asyncio.run(run(args.audio_path, args.patient_id, args.auto_approve))


if __name__ == "__main__":
    sys.exit(main())
