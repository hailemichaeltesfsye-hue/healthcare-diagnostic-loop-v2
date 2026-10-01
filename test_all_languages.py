import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.agents.compliance import ComplianceAgent
from src.graph.state import SharedState


TESTS = {
    "en": {
        "raw": "I have severe headache and dizziness.",
        "symptoms": ["severe headache", "dizziness"],
        "diagnosis": "Possible hypertension",
    },
    "am": {
        "raw": "ከባድ የራስ ምታት እና ማዞር አለኝ።",
        "symptoms": ["severe headache", "dizziness"],
        "diagnosis": "Possible hypertension",
    },
    "ar": {
        "raw": "أشعر بألم شديد في المعدة مع الغثيان وفقدان الشهية.",
        "symptoms": ["severe stomach pain", "nausea", "loss of appetite"],
        "diagnosis": "Possible gastrointestinal condition",
    },
    "zh": {
        "raw": "我有严重的头痛和头晕。",
        "symptoms": ["severe headache", "dizziness"],
        "diagnosis": "Possible hypertension",
    },
    "fr": {
        "raw": "J'ai de graves maux de tête et des vertiges.",
        "symptoms": ["severe headache", "dizziness"],
        "diagnosis": "Possible hypertension",
    },
    "hi": {
        "raw": "मुझे तेज़ सिरदर्द और चक्कर आ रहे हैं।",
        "symptoms": ["severe headache", "dizziness"],
        "diagnosis": "Possible hypertension",
    },
}


async def main():
    agent = ComplianceAgent()

    for language, data in TESTS.items():
        state = SharedState(
            patient_id=f"TEST-{language.upper()}-001",
            raw_symptoms=data["raw"],
            extracted_symptoms=data["symptoms"],
            initial_diagnosis=data["diagnosis"],
            detected_language_code=language,
            hitl_approved=True,
        )

        result = await agent.process(state)

        print("\n" + "=" * 60)
        print(f"LANGUAGE: {language}")
        print("=" * 60)
        print(result["final_clinical_report"])


asyncio.run(main())
