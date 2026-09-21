"""Canonical language metadata shared by the transcription and synthesis services.

Keeping this table in one place means the AssemblyAI language code the loop
detects on the way in is guaranteed to resolve to a matching gTTS voice on the
way out, instead of two services drifting out of sync with their own private
language lists.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageProfile:
    """Describes one clinically-supported spoken language end-to-end."""

    display_name: str
    assemblyai_code: str
    gtts_code: str
    flag_emoji: str = "🌐"


# The six languages this loop explicitly commits to supporting end-to-end.
# AssemblyAI's automatic language detection covers ~99 languages, so
# detection may return a code outside this table; see
# ``resolve_language_profile`` below for the fallback behavior in that case.
SUPPORTED_CLINICAL_LANGUAGES: dict[str, LanguageProfile] = {
    "en": LanguageProfile(display_name="English", assemblyai_code="en", gtts_code="en", flag_emoji="🇬🇧"),
    "am": LanguageProfile(display_name="Amharic", assemblyai_code="am", gtts_code="am", flag_emoji="🇪🇹"),
    "ar": LanguageProfile(display_name="Arabic", assemblyai_code="ar", gtts_code="ar", flag_emoji="🇸🇦"),
    "zh": LanguageProfile(display_name="Chinese", assemblyai_code="zh", gtts_code="zh-CN", flag_emoji="🇨🇳"),
    "fr": LanguageProfile(display_name="French", assemblyai_code="fr", gtts_code="fr", flag_emoji="🇫🇷"),
    "hi": LanguageProfile(display_name="Hindi", assemblyai_code="hi", gtts_code="hi", flag_emoji="🇮🇳"),
}

DEFAULT_LANGUAGE_CODE = "en"


def resolve_language_profile(detected_code: str | None) -> tuple[LanguageProfile, bool]:
    """Map a raw AssemblyAI language code onto a clinically-supported profile.

    Returns a tuple of ``(profile, was_exact_match)``. When AssemblyAI detects
    a language outside the six this loop is contracted to support, the loop
    degrades to English rather than failing the whole voice round-trip, and
    the caller is told via ``was_exact_match=False`` so it can log/flag the
    degradation for clinical review.
    """
    if not detected_code:
        return SUPPORTED_CLINICAL_LANGUAGES[DEFAULT_LANGUAGE_CODE], False

    normalized = detected_code.strip().lower().split("-")[0]
    profile = SUPPORTED_CLINICAL_LANGUAGES.get(normalized)
    if profile is not None:
        return profile, True
    return SUPPORTED_CLINICAL_LANGUAGES[DEFAULT_LANGUAGE_CODE], False
