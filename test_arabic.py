import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.agents.compliance import ComplianceAgent
from src.graph.state import SharedState


async def main():
    agent = ComplianceAgent()

    state = SharedState(
        patient_id="TEST-AR-001",
        raw_symptoms="أشعر بألم شديد في المعدة مع الغثيان وفقدان الشهية منذ ثلاثة أيام.",
        extracted_symptoms=[
            "severe stomach pain",
            "nausea",
            "loss of appetite",
        ],
        initial_diagnosis="Possible gastrointestinal condition",
        detected_language_code="ar",
        hitl_approved=True,
    )

    result = await agent.process(state)

    print("\n==============================")
    print("ARABIC TEST")
    print("==============================")
    print(result["final_clinical_report"])


asyncio.run(main())
