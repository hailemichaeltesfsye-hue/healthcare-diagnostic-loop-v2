"""Static, per-language halt notices for compliance-blocked cases.

When PII/PHI or legal-liability language is detected, the patient still
needs to hear *something* in their own language via the voice loop - but at
that point we deliberately want to send zero patient content to any
third-party LLM. These are fixed, non-LLM-generated templates so the halt
notice is available with zero data exposure and zero dependency on an
external API being up.

CAUTION: these were authored for this project, not reviewed by native
speakers or clinical/compliance staff. Before production use, have a native
speaker (and your compliance team) review the wording in every language you
actually serve.
"""

from __future__ import annotations

HALT_TEMPLATES: dict[str, str] = {
    "en": (
        "Your case is currently under a routine compliance review before we "
        "can share your report. A member of our clinical team will follow up "
        "with you shortly."
    ),
    "am": (
        "ጉዳይዎ ሪፖርቱ ከመጋራታችን በፊት በመደበኛ የተገዢነት ግምገማ ውስጥ ነው። "
        "የክሊኒክ ቡድናችን አባል በቅርቡ ያነጋግርዎታል።"
    ),
    "ar": (
        "حالتك قيد المراجعة الروتينية للامتثال حاليًا قبل أن نتمكن من مشاركة "
        "تقريرك. سيتواصل معك أحد أعضاء فريقنا السريري قريبًا."
    ),
    "zh": (
        "在我们分享您的报告之前，您的病例目前正在接受常规合规审查。"
        "我们的临床团队成员将很快与您联系。"
    ),
    "fr": (
        "Votre dossier fait actuellement l'objet d'un contrôle de conformité "
        "de routine avant que nous puissions partager votre rapport. Un "
        "membre de notre équipe clinique vous contactera sous peu."
    ),
    "hi": (
        "आपकी रिपोर्ट साझा करने से पहले आपका मामला वर्तमान में नियमित "
        "अनुपालन समीक्षा के अधीन है। हमारी क्लिनिकल टीम का एक सदस्य जल्द ही "
        "आपसे संपर्क करेगा।"
    ),
}

DEFAULT_HALT_MESSAGE = HALT_TEMPLATES["en"]


def get_halt_message(language_code: str) -> str:
    """Return the halt notice for ``language_code``, defaulting to English."""
    return HALT_TEMPLATES.get(language_code, DEFAULT_HALT_MESSAGE)
