"""Shared Groq chat-completions client for clinical reasoning agents.

Every agent that needs real LLM reasoning (triage extraction, diagnostic
Tree-of-Thoughts, compliance screening) goes through this one hardened path
instead of each hand-rolling its own client, retry policy, and JSON parsing.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict

try:
    from groq import APIConnectionError, APIStatusError, Groq, RateLimitError
except ImportError as exc:  # pragma: no cover - surfaced at call time instead
    Groq = None
    APIConnectionError = APIStatusError = RateLimitError = Exception
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

# Matches the model already verified against this project's Groq account in
# scripts/test_groq.py. Override with GROQ_MODEL if your account differs.
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 0.75

# Rough placeholder rate — Groq pricing varies by model and changes over
# time. This only feeds the existing token_usage_log dashboard; confirm the
# real figure against your account's billing page before trusting the
# aggregate cost total for anything financial.
ROUGH_COST_PER_1K_TOKENS = 0.0002


class LLMReasoningError(RuntimeError):
    """Raised when the Groq-backed reasoning call cannot produce a usable result.

    Every agent that uses this client is expected to catch this specific
    exception and fall back to its deterministic rule-based logic rather than
    letting a transient LLM outage take down the whole diagnostic loop.
    """


class GroqReasoningClient:
    """Minimal JSON-mode chat client with retries, used by the clinical agents."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        if Groq is None:
            raise LLMReasoningError(
                "The 'groq' package is not installed. Run `uv pip install groq` "
                "(it is already listed in pyproject.toml, so `uv pip install -e .` "
                "should cover it)."
            ) from _IMPORT_ERROR

        resolved_key = api_key or os.getenv("GROQ_API_KEY")
        if not resolved_key:
            raise LLMReasoningError(
                "No Groq API key configured. Set GROQ_API_KEY in the environment "
                "or .env file."
            )

        self._client = Groq(api_key=resolved_key)
        self._model = model

    def _complete_json_sync(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Blocking call intended to run inside ``asyncio.to_thread``."""
        last_error: Exception | None = None
        response = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                )
                break
            except RateLimitError as exc:
                last_error = exc
            except APIConnectionError as exc:
                last_error = exc
            except APIStatusError as exc:
                # Non-transient (auth, bad request, etc.) — do not retry.
                raise LLMReasoningError(f"Groq API rejected the request: {exc}") from exc
            except Exception as exc:  # Defensive: unknown SDK failure modes.
                raise LLMReasoningError(f"Unexpected Groq client failure: {exc}") from exc

            if attempt < _MAX_ATTEMPTS:
                time.sleep(_BACKOFF_SECONDS * attempt)

        if response is None:
            raise LLMReasoningError(
                f"Groq request failed after {_MAX_ATTEMPTS} attempts: {last_error}"
            )

        choice = response.choices[0]
        raw_content = choice.message.content or ""
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise LLMReasoningError(
                "Groq returned non-JSON content despite json_object mode: "
                f"{raw_content[:200]!r}"
            ) from exc

        if not isinstance(parsed, dict):
            raise LLMReasoningError(
                f"Groq returned a JSON value that was not an object: {parsed!r}"
            )

        usage = getattr(response, "usage", None)
        parsed["_usage"] = {
            "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        }
        return parsed

    async def complete_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Run one JSON-mode completion off the event loop.

        Raises :class:`LLMReasoningError` for every failure mode (auth,
        network, rate limit exhaustion, malformed JSON) so callers have a
        single exception type to catch for their fallback path.
        """
        try:
            return await asyncio.to_thread(self._complete_json_sync, system_prompt, user_prompt)
        except LLMReasoningError:
            raise
        except Exception as exc:  # Defensive: never let a raw error escape.
            raise LLMReasoningError(f"Unexpected reasoning failure: {exc}") from exc


def build_token_log(node_name: str, usage: Dict[str, Any]) -> Dict[str, Any]:
    """Build a token_usage_log entry from a Groq response's ``_usage`` payload."""
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    total_tokens = input_tokens + output_tokens
    return {
        "node": node_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost": round((total_tokens / 1000) * ROUGH_COST_PER_1K_TOKENS, 6),
    }
