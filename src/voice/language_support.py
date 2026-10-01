"""Canonical language metadata shared across transcription, LLM reasoning, and synthesis services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class LanguageProfile:
    """Describes one clinically-supported language end-to-end across the voice pipeline."""

    language_code: str
    display_name: str
    native_name: str
    locale: str
    assemblyai_code: str
    gtts_code: str
    flag_emoji: str = "🌐"
    browser_voice_tag: str = "en-US"
    tts_tlds: Sequence[str] = ("com", "co.uk", "ca")
    llm_instruction: str = ""
    disclaimer: str = ""
    emergency_warning: str = ""
    sample_symptom: str = ""
    sample_emergency: str = ""


SUPPORTED_CLINICAL_LANGUAGES: dict[str, LanguageProfile] = {
    "en": LanguageProfile(
        language_code="en",
        display_name="English",
        native_name="English",
        locale="en-US",
        assemblyai_code="en",
        gtts_code="en",
        flag_emoji="🇬🇧",
        browser_voice_tag="en-US",
        tts_tlds=("com", "co.uk", "ca"),
        llm_instruction=(
            "Respond entirely in English. Maintain an empathetic, professional clinical "
            "tone. Ask relevant follow-up questions to understand severity and duration. "
            "Never claim to be a physician or provide a definitive medical diagnosis. "
            "Always include safe next-step guidance."
        ),
        disclaimer=(
            "⚠️ Disclaimer: I am an AI healthcare assistant, not a doctor. This guidance "
            "is for informational support and does not constitute a definitive medical diagnosis. "
            "If you are experiencing life-threatening symptoms, please call emergency services immediately."
        ),
        emergency_warning=(
            "🚨 CRITICAL RED-FLAG ALERT: Your reported symptoms indicate a potential medical emergency. "
            "Please call 911 (or your local emergency services) or go to the nearest emergency department immediately."
        ),
        sample_symptom="I have had a throbbing tension headache and trouble sleeping for the past 2 days.",
        sample_emergency="I have sudden severe crushing chest pain radiating down my left arm and I can barely breathe.",
    ),
    "am": LanguageProfile(
        language_code="am",
        display_name="Amharic",
        native_name="አማርኛ",
        locale="am-ET",
        assemblyai_code="am",
        gtts_code="am",
        flag_emoji="🇪🇹",
        browser_voice_tag="am-ET",
        tts_tlds=("com", "co.uk"),
        llm_instruction=(
            "ሙሉ በሙሉ በአማርኛ ቋንቋ ብቻ መልስ ይስጡ። ርኅራኄ የተሞላበት እና ሙያዊ የሕክምና ግንኙነት ዘይቤን ይጠቀሙ። "
            "ፈጽሞ ሐኪም እንደሆኑ አድርገው አይናገሩ ወይም የመጨረሻ የሕክምና ውሳኔ አይስጡ። "
            "የሕመሙን ክብደት እና ቆይታ ለመረዳት አግባብነት ያላቸውን ተከታይ ጥያቄዎችን ይጠይቁ።"
        ),
        disclaimer=(
            "⚠️ ማስተባበያ፡ እኔ የኤአይ ጤና ረዳት ነኝ እንጂ ሐኪም አይደለሁም። ይህ መረጃ ለግንዛቤ ድጋፍ ብቻ የቀረበ ነው፤ "
            "የሕክምና ምርመራን አይተካም። ድንገተኛ አደጋ ካጋጠመዎት እባክዎ ወዲያውኑ ወደ ድንገተኛ ሕክምና አገልግሎት ይደውሉ።"
        ),
        emergency_warning=(
            "🚨 አስቸኳይ የጤና ማስጠንቀቂያ፡ የገለጿቸው ምልክቶች አስቸኳይ የሕክምና እርዳታ የሚያስፈልጋቸውን ሁኔታዎች ያመለክታሉ። "
            "እባክዎ አሁኑኑ በአቅራቢያዎ ወደሚገኝ የድንገተኛ ክፍል ይሂዱ ወይም ወደ ድንገተኛ ሕክምና ስልክ ይደውሉ።"
        ),
        sample_symptom="ላለፉት ሁለት ቀናት ከባድ የራስ ምታት እና ማዞር አለብኝ።",
        sample_emergency="በጣም ከባድ የደረት ሕመም አለብኝ፣ ወደ ግራ እጄ የሚሰራጭ እና ለመተንፈስ እያስቸገረኝ ነው።",
    ),
    "ar": LanguageProfile(
        language_code="ar",
        display_name="Arabic",
        native_name="العربية",
        locale="ar-SA",
        assemblyai_code="ar",
        gtts_code="ar",
        flag_emoji="🇸🇦",
        browser_voice_tag="ar-SA",
        tts_tlds=("com", "co.uk", "ca"),
        llm_instruction=(
            "أجب باللغة العربية الفصحى حصراً وبأسلوب متعاطف ومهني. "
            "لا تدَّعِ أنك طبيب بشري ولا تقدم تشخيصاً قاطعاً. "
            "اطرح أسئلة متابعة واضحة عن حدة الأعراض ومدتها وقدّم إرشادات وقائية آمنة."
        ),
        disclaimer=(
            "⚠️ إخلاء مسؤولية: أنا مساعد رعاية صحية ذكي ولست طبيباً بشرياً. "
            "هذه المعلومات لأغراض التوجيه فقط ولا تعتبر تشخيصاً طبياً نهائياً. "
            "في حالات الطوارئ يرجى الاتصال بالإسعاف فوراً."
        ),
        emergency_warning=(
            "🚨 تنبيه طوارئ حرج: الأعراض التي وصفتها تشير إلى احتمال وجود حالة طبية طارئة. "
            "يرجى التوجه إلى قسم الطوارئ فوراً أو الاتصال بالإسعاف على الفور."
        ),
        sample_symptom="أشعر بألم معتدل في المعدة مع غثيان خفيف منذ البارحة.",
        sample_emergency="أعاني من ألم حاد ومفاجئ في الصدر ينتشر إلى الذراع الأيسر مع ضيق شديد في التنفس.",
    ),
    "zh": LanguageProfile(
        language_code="zh",
        display_name="Chinese",
        native_name="中文",
        locale="zh-CN",
        assemblyai_code="zh",
        gtts_code="zh-CN",
        flag_emoji="🇨🇳",
        browser_voice_tag="zh-CN",
        tts_tlds=("com", "co.uk"),
        llm_instruction=(
            "完全使用简体中文回答。保持专业且富有同理心的临床沟通语气。"
            "切勿冒充医生或提供终局医疗诊断。主动询问症状持续时间与严重程度，"
            "并提供安全可行的下一步分诊建议。"
        ),
        disclaimer=(
            "⚠️ 免责声明：我是AI健康语音助手，并非专业医生。本建议仅供健康咨询与初步分诊参考，"
            "不能替代正规医学诊断。如遇紧急医疗情况，请立即拨打急救电话。"
        ),
        emergency_warning=(
            "🚨 严重紧急预警：您所描述的症状可能提示危急医疗情况。请立即拨打120急救电话或前往最近的医院急诊科就医。"
        ),
        sample_symptom="我这两天一直有些轻微头晕和喉咙不适，伴有轻度乏力。",
        sample_emergency="我突然感到剧烈胸痛并伴有左臂放射性麻木，呼吸极度困难。",
    ),
    "fr": LanguageProfile(
        language_code="fr",
        display_name="French",
        native_name="Français",
        locale="fr-FR",
        assemblyai_code="fr",
        gtts_code="fr",
        flag_emoji="🇫🇷",
        browser_voice_tag="fr-FR",
        tts_tlds=("com", "fr", "ca"),
        llm_instruction=(
            "Répondez entièrement en français avec empathie et rigueur clinique. "
            "Ne prétendez jamais être un médecin et ne posez aucun diagnostic définitif. "
            "Posez des questions de suivi pertinentes sur la durée et l'intensité des symptômes, "
            "et fournissez des conseils sécurisés sur les prochaines démarches."
        ),
        disclaimer=(
            "⚠️ Avertissement : Je suis un assistant vocal d'orientation santé propulsé par l'IA et non un médecin. "
            "Ces informations ne constituent pas un diagnostic médical. En cas d'urgence, contactez immédiatement les services de secours."
        ),
        emergency_warning=(
            "🚨 ALERTE URGENCE VITALE : Vos symptômes peuvent indiquer une urgence médicale immédiate. "
            "Veuillez composer le 15 / 112 ou vous rendre immédiatement aux urgences les plus proches."
        ),
        sample_symptom="J'ai des maux de tête légers et une fatigue inhabituelle depuis deux jours.",
        sample_emergency="J'ai une douleur thoracique soudaine et intense qui irradie vers mon bras gauche et du mal à respirer.",
    ),
    "hi": LanguageProfile(
        language_code="hi",
        display_name="Hindi",
        native_name="हिन्दी",
        locale="hi-IN",
        assemblyai_code="hi",
        gtts_code="hi",
        flag_emoji="🇮🇳",
        browser_voice_tag="hi-IN",
        tts_tlds=("com", "co.in", "co.uk"),
        llm_instruction=(
            "उत्तर पूरी तरह से सरल और स्पष्ट हिंदी में दें। एक संवेदनशील और पेशेवर लहजा बनाए रखें। "
            "खुद को डॉक्टर न बताएं और न ही कोई अंतिम चिकित्सा निदान दें। "
            "लक्षणों की गंभीरता और अवधि को समझने के लिए उपयुक्त अनुवर्ती प्रश्न पूछें और सुरक्षित मार्गदर्शन दें।"
        ),
        disclaimer=(
            "⚠️ अस्वीकरण: मैं एक एआई स्वास्थ्य सहायक हूँ, कोई चिकित्सक (डॉक्टर) नहीं। "
            "यह जानकारी केवल परामर्श और मार्गदर्शन के लिए है, इसे अंतिम चिकित्सा निदान न मानें। "
            "आपातकालीन स्थिति में तुरंत निकटतम अस्पताल या आपातकालीन सेवा से संपर्क करें।"
        ),
        emergency_warning=(
            "🚨 आपातकालीन चेतावनी: आपके लक्षण एक गंभीर आपातकालीन स्थिति का संकेत हो सकते हैं। "
            "कृपया तुरंत आपातकालीन नंबर पर कॉल करें या नजदीकी अस्पताल के आपातकालीन विभाग में जाएं।"
        ),
        sample_symptom="मुझे पिछले दो दिनों से हल्का सिरदर्द और थकान महसूस हो रही है।",
        sample_emergency="मेरे सीने में अचानक बहुत तेज दर्द हो रहा है जो बाएं हाथ तक फैल रहा है और सांस लेने में कठिनाई हो रही है।",
    ),
}

DEFAULT_LANGUAGE_CODE = "en"


def resolve_language_profile(
    detected_code: str | None,
) -> tuple[LanguageProfile, bool]:
    """Resolve an AssemblyAI or standard ISO language code to a supported language profile."""
    normalized = (detected_code or "").strip().lower()

    if "-" in normalized:
        normalized = normalized.split("-", 1)[0]
    if "_" in normalized:
        normalized = normalized.split("_", 1)[0]

    profile = SUPPORTED_CLINICAL_LANGUAGES.get(normalized)
    if profile is None:
        return (
            SUPPORTED_CLINICAL_LANGUAGES[DEFAULT_LANGUAGE_CODE],
            False,
        )

    return profile, True


def get_language_profile(code: str) -> LanguageProfile:
    """Convenience getter returning the profile for a given code (defaults to English)."""
    profile, _ = resolve_language_profile(code)
    return profile
