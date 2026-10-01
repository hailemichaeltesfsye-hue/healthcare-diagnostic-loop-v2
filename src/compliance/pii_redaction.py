"""Deterministic PII/PHI redaction, applied before any patient text reaches a
third-party LLM.

The original compliance agent asked the LLM itself to judge whether the
patient's statement contained PII or legal-liability language. That has two
problems: it's unreliable (an LLM can miss or hallucinate), and it requires
sending the raw sensitive text to a third party just to find out whether it
was sensitive. Regex-based redaction is auditable, testable offline, and
lets the risk decision be made in Python *before* anything is sent anywhere.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
# 13-19 digits, optionally grouped with spaces/dashes - generic card-number shape.
_CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
# Any other run of 6+ consecutive digits: national IDs, MRNs, account numbers.
# Deliberately broad - over-redacting a long lab value is a safer failure mode
# than under-redacting a real identifier.
_LONG_ID_RE = re.compile(r"\b\d{6,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b")
_NAME_INTRO_RE = re.compile(r"(?<=\bmy name is\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE)
_LEGAL_RISK_RE = re.compile(
    r"\b(sue|suing|sued|lawsuit|lawyer|attorney|litigation|malpractice)\b",
    re.IGNORECASE,
)

# Order matters: more specific patterns run first so they claim their own
# placeholder before the generic long-digit catch-all would swallow them.
_REDACTION_PATTERNS = (
    (_EMAIL_RE, "[REDACTED_EMAIL]"),
    (_SSN_RE, "[REDACTED_SSN]"),
    (_CREDIT_CARD_RE, "[REDACTED_CARD]"),
    (_LONG_ID_RE, "[REDACTED_ID]"),
    (_PHONE_RE, "[REDACTED_PHONE]"),
    (_NAME_INTRO_RE, "[REDACTED_NAME]"),
)


@dataclass
class RedactionResult:
    """Outcome of scanning one piece of patient-provided text."""

    redacted_text: str
    pii_detected: bool
    legal_risk_detected: bool
    reasons: List[str] = field(default_factory=list)


def redact_pii(text: str) -> RedactionResult:
    """Strip common PII/PHI patterns and flag legal-liability language.

    This is intentionally conservative pattern matching, not an NLP entity
    recognizer - it will not catch everything (e.g. a name on its own,
    without an accompanying identifier), and it may occasionally redact
    something that wasn't actually sensitive (e.g. a long lab value). Treat
    it as one layer of defense-in-depth, not a complete PHI de-identification
    solution.
    """
    if not text:
        return RedactionResult(redacted_text=text, pii_detected=False, legal_risk_detected=False)

    redacted = text
    reasons: List[str] = []
    for pattern, placeholder in _REDACTION_PATTERNS:
        if pattern.search(redacted):
            reasons.append(f"Matched pattern for {placeholder}")
            redacted = pattern.sub(placeholder, redacted)

    legal_risk = bool(_LEGAL_RISK_RE.search(text))
    if legal_risk:
        reasons.append("Legal-liability language detected")

    return RedactionResult(
        redacted_text=redacted,
        pii_detected=bool(reasons) and any("REDACTED" in reason for reason in reasons),
        legal_risk_detected=legal_risk,
        reasons=reasons,
    )
