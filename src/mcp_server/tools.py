"""
Core mock tool infrastructure simulating deep Model Context Protocol data services.

The deterministic in-process implementation provides a stable Part 1 contract
for later agent orchestration while keeping tool inputs and outputs explicit.
"""

from typing import Any, Dict, List


class MedicalKnowledgeBase:
    """Provide verified clinical guideline and interaction lookups."""

    @staticmethod
    def get_guidelines(conditions: List[str]) -> str:
        """
        Return guideline text for recognized conditions.

        Unknown conditions are intentionally handled with a conservative
        standard-care pathway rather than silently returning an empty result.
        """
        guidelines: Dict[str, str] = {
            "hypertension": (
                "First-line: ACE inhibitors or ARBs. Monitor serum creatinine "
                "and potassium levels regularly."
            ),
            "diabetes": (
                "First-line: Metformin titrated up to 2000mg/day. Baseline HbA1c "
                "screening required every 3 months."
            ),
            "migraine": (
                "Acute treatment: Triptans. Preventative tracking via Beta-blockers "
                "or Topiramate if episodes >4/month."
            ),
            "insomnia": (
                "Implement Cognitive Behavioral Therapy for Insomnia (CBT-I) "
                "protocols before sedative pharmacotherapy."
            ),
        }
        found = [guidelines[condition.lower()] for condition in conditions if condition.lower() in guidelines]
        if not found:
            return (
                "Standard internal care pathway blueprint: Monitor vitals, check "
                "baseline metabolic panels, and advise rest."
            )
        return " | ".join(found)

    @staticmethod
    def check_interactions(drugs: List[str]) -> Dict[str, Any]:
        """
        Check the supported high-risk medication combinations.

        Drug names are normalized case-insensitively. The returned dictionary
        always contains a status and conflict list for predictable downstream
        serialization.
        """
        normalized = [drug.lower() for drug in drugs]
        result: Dict[str, Any] = {"status": "SAFE", "conflicts": []}

        if "metformin" in normalized and "contrast_dye" in normalized:
            result["status"] = "HIGH_RISK"
            result["conflicts"].append(
                "Metformin + Contrast Dye: High risk of severe Lactic Acidosis. "
                "Suspend drug 48h before procedure."
            )
        if "lisinopril" in normalized and "spironolactone" in normalized:
            result["status"] = "MODERATE_RISK"
            result["conflicts"].append(
                "Lisinopril + Spironolactone: Synergistic hyperkalemia risk. "
                "Active serum potassium telemetry required."
            )

        return result