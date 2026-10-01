"""Deterministic and clinical emergency / red-flag triage detection layer.

Screens patient symptoms for life-threatening presentations (cardiovascular,
respiratory, neurological/stroke, hemorrhagic, anaphylaxis, acute crisis)
across all supported languages. Enforces medical disclaimers and immediate
escalation pathways.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import List, Sequence

from src.voice.language_support import get_language_profile, resolve_language_profile


class RiskLevel(str, enum.Enum):
    """Clinical risk classification."""

    EMERGENCY = "EMERGENCY"  # Immediate life-threat; seek 911 / emergency care immediately
    URGENT = "URGENT"        # Needs prompt clinical evaluation within hours
    ROUTINE = "ROUTINE"      # Low-risk; conservative guidance & schedule clinic visit


@dataclass
class TriageAssessment:
    """Structured clinical safety output evaluated before or during voice reasoning."""

    risk_level: RiskLevel
    is_emergency: bool
    category: str
    matched_flags: List[str]
    immediate_guidance: str
    localized_alert: str
    disclaimer: str


# Comprehensive red-flag keyword triggers categorized across languages
_RED_FLAG_PATTERNS: dict[str, Sequence[str]] = {
    "cardiovascular": [
        "chest pain", "crushing chest", "heart attack", "radiating to left arm",
        "pressure in chest", "chest tightness", "pain in jaw and chest",
        "የደረት ሕመም", "የልብ ሕመም", "የደረት መወጠር",  # Amharic
        "ألم في الصدر", "ذبحة صدرية", "نوبة قلبية", "ألم الصدر",  # Arabic
        "胸痛", "心肌梗塞", "心脏剧痛", "胸部压迫感",  # Chinese
        "douleur thoracique", "douleur à la poitrine", "crise cardiaque", "infarctus",  # French
        "सीने में दर्द", "हार्ट अटैक", "सीने में भारीपन", "दिल का दौरा",  # Hindi
    ],
    "respiratory": [
        "cannot breathe", "can't breathe", "shortness of breath", "gasping for air",
        "severe breathlessness", "lips turning blue", "suffocating", "stridor",
        "መተንፈስ አቃተኝ", "የመተንፈስ ችግር", "ትንፋሽ ማጠር",  # Amharic
        "ضيق شديد في التنفس", "لا أستطيع التنفس", "اختناق",  # Arabic
        "无法呼吸", "极度呼吸困难", "窒息感", "喘不上气",  # Chinese
        "difficulté à respirer", "ne peux pas respirer", "étouffement", "détresse respiratoire",  # French
        "सांस नहीं आ रही", "सांस लेने में भारी तकलीफ", "दम घुट रहा है",  # Hindi
    ],
    "stroke_neurological": [
        "face drooping", "slurred speech", "sudden numbness", "arm weakness",
        "cannot speak", "facial numbness", "stroke", "worst headache of my life",
        "thunderclap headache", "sudden paralysis", "loss of vision",
        "የፊት መደንዘዝ", "መናገር አቃተኝ", "የሰውነት መጎተት", "ስትሮክ",  # Amharic
        "شلل نصفي", "صعوبة في النطق", "تنميل مفاجئ", "جلطة دماغية",  # Arabic
        "面瘫", "说话不清", "突发偏瘫", "一侧肢体无力", "中风", "脑梗",  # Chinese
        "paralysie faciale", "difficulté à parler", "engourdissement soudain", "accident vasculaire cérébral", "avc",  # French
        "चेहरा सुन्न होना", "बोलने में लड़खड़ाहट", "अचानक लकवा", "स्ट्रोक", "अंगों की कमजोरी",  # Hindi
    ],
    "consciousness_seizure": [
        "loss of consciousness", "unconscious", "passed out", "blacked out",
        "fainted and unresponsive", "seizure", "convulsing",
        "ራሴን ሳትኩ", "የሚጥል በሽታ", "መንቀጥቀጥ",  # Amharic
        "فقدان الوعي", "إغماء", "تشنجات", "صرع",  # Arabic
        "意识丧失", "晕厥不醒", "癫痫发作", "抽搐",  # Chinese
        "perte de connaissance", "évanouissement", "inconscient", "convulsions",  # French
        "बेहोश हो जाना", "होश खो बैठना", "दौरा पड़ना", "मिर्गी का दौरा",  # Hindi
    ],
    "severe_bleeding": [
        "coughing up blood", "vomiting blood", "severe bleeding", "uncontrolled bleeding",
        "blood spurting", "hemoptysis", "hematemesis",
        "ደም ማስታወክ", "ከፍተኛ ደም መፍሰስ", "ደም ማሳል",  # Amharic
        "نزيف حاد", "بصق دم", "تقيؤ دم", "نزيف لا يتوقف",  # Arabic
        "大出血", "咳血", "吐血", "血流不止",  # Chinese
        "hémorragie sévère", "cracher du sang", "vomir du sang", "saignement incontrôlable",  # French
        "खून की उल्टी", "खांसी में खून", "तेज रक्तस्राव", "खून बहना बंद न होना",  # Hindi
    ],
    "anaphylaxis": [
        "throat closing", "throat swelling", "swollen tongue", "anaphylaxis",
        "allergic reaction cannot breathe",
        "የጉሮሮ ማበጥ", "የአለርጂ አስቸኳይ ሁኔታ",  # Amharic
        "تورم الحلق", "صدمة تحسسية", "حساسية مفرطة وانغلاق الحلق",  # Arabic
        "喉头水肿", "严重过敏反应无法呼吸", "气道梗阻",  # Chinese
        "gonflement de la gorge", "choc anaphylactique", "œdème de quincke",  # French
        "गला सूज जाना", "गंभीर एलर्जी के कारण सांस रुकना",  # Hindi
    ],
    "acute_crisis": [
        "want to kill myself", "suicidal", "want to end my life", "suicide",
        "self harm",
        "ራሴን ማጥፋት እፈልጋለሁ",  # Amharic
        "أريد الانتحار", "أفكار انتحارية",  # Arabic
        "自杀", "想要自杀", "想要结束生命",  # Chinese
        "envie de mourir", "idées suicidaires", "me suicider",  # French
        "आत्महत्या", "खुद को मारना चाहता हूँ",  # Hindi
    ],
}

# Moderate / Urgent keywords
_URGENT_PATTERNS: Sequence[str] = [
    "high fever", "persistent vomiting", "cannot keep fluids down",
    "severe abdominal pain", "blood in stool", "blood in urine",
    "stiff neck and fever", "confusion", "deep laceration",
    "ከፍተኛ ትኩሳት", "ከባድ የሆድ ሕመም",  # Amharic
    "حمى شديدة", "ألم حاد في البطن", "قيء مستمر",  # Arabic
    "高烧不退", "剧烈腹痛", "持续呕吐",  # Chinese
    "forte fièvre", "douleur abdominale intense",  # French
    "तेज बुखार", "पेट में असहनीय दर्द",  # Hindi
]


class EmergencyDetector:
    """Evaluates symptoms for life-threatening emergencies and safety risks."""

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        symptoms_text: str,
        language_code: str | None = "en",
    ) -> TriageAssessment:
        """Scan input text against clinical red flags and determine risk level."""
        text_lower = (symptoms_text or "").lower()
        matched_flags: List[str] = []
        primary_category = "General Medical Triage"

        # Check critical emergency patterns
        for category, patterns in _RED_FLAG_PATTERNS.items():
            for pattern in patterns:
                # Use word boundary where appropriate or simple substring
                if pattern.lower() in text_lower:
                    matched_flags.append(f"{category.replace('_', ' ').title()}: '{pattern}'")
                    primary_category = category.replace("_", " ").title()

        profile = get_language_profile(language_code or "en")

        if matched_flags:
            # Life-threatening emergency detected!
            return TriageAssessment(
                risk_level=RiskLevel.EMERGENCY,
                is_emergency=True,
                category=primary_category,
                matched_flags=matched_flags,
                immediate_guidance=(
                    "CRITICAL: Immediate emergency medical intervention is required. "
                    "Do NOT delay or wait for routine appointments. Call emergency services immediately."
                ),
                localized_alert=profile.emergency_warning,
                disclaimer=profile.disclaimer,
            )

        # Check moderate/urgent patterns
        for pattern in _URGENT_PATTERNS:
            if pattern.lower() in text_lower:
                matched_flags.append(f"Urgent Care: '{pattern}'")

        if matched_flags:
            return TriageAssessment(
                risk_level=RiskLevel.URGENT,
                is_emergency=False,
                category="Urgent Care Escalation",
                matched_flags=matched_flags,
                immediate_guidance=(
                    "Your symptoms indicate conditions that require prompt in-person medical "
                    "evaluation within 12-24 hours at an urgent care clinic or doctor's office."
                ),
                localized_alert=(
                    f"⚠️ Notice: Prompt clinical evaluation is advised. {profile.disclaimer}"
                ),
                disclaimer=profile.disclaimer,
            )

        # Routine / low-risk
        return TriageAssessment(
            risk_level=RiskLevel.ROUTINE,
            is_emergency=False,
            category="Low-Risk Symptom Consultation",
            matched_flags=[],
            immediate_guidance=(
                "Your symptoms appear to be non-emergent. Focus on monitoring changes, "
                "rest, hydration, and consult your primary healthcare practitioner if symptoms persist."
            ),
            localized_alert="",
            disclaimer=profile.disclaimer,
        )
