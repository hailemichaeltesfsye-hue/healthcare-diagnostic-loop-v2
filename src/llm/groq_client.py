"""Unified Groq client for clinical reasoning agents.

Consolidates LLM interaction, JSON-mode parsing, exponential backoff, and
token/cost accounting so that individual agents stay focused on their own
clinical logic instead of re-implementing client plumbing.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

try:
    from groq import APIConnectionError, APIStatusError, Groq, RateLimitError
except ImportError as exc:  # pragma: no cover - surfaced at call time instead
    Groq = None  # type: ignore[assignment,misc]
    APIConnectionError = Exception  # type: ignore[assignment,misc]
    APIStatusError = Exception  # type: ignore[assignment,misc]
    RateLimitError = Exception  # type: ignore[assignment,misc]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


# Default model used across clinical reasoning agents.
DEFAULT_MODEL = "openai/gpt-oss-120b"

# Pricing per 1M tokens for openai/gpt-oss-120b (as tracked across the loop).
# Kept here as the single source of truth for cost calculations.
COST_PER_MILLION_INPUT_TOKENS = 0.15
COST_PER_MILLION_OUTPUT_TOKENS = 0.60


class LLMReasoningError(RuntimeError):
    """Raised when the LLM cannot produce a valid reasoning output.

    Agents catch this exception specifically to trigger their deterministic
    fallback paths (rule-based symptom extraction, heuristic scoring, etc.).
    """


class GroqReasoningClient:
    """Thread-safe, retrying Groq client specialized for structured clinical JSON."""

    _DEFAULT_MODEL = DEFAULT_MODEL
    _MAX_RETRIES = 3
    _BASE_BACKOFF_SECONDS = 0.5

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        if Groq is None:
            raise LLMReasoningError(
                "The 'groq' package is not installed. Install it with "
                "`uv pip install groq` (or `pip install groq`) and retry."
            ) from _IMPORT_ERROR

        resolved_key = api_key or os.getenv("GROQ_API_KEY")
        if not resolved_key:
            raise LLMReasoningError(
                "No Groq API key was provided. Set the GROQ_API_KEY environment "
                "variable or pass api_key= explicitly to GroqReasoningClient."
            )

        model = model or os.getenv("GROQ_MODEL") or self._DEFAULT_MODEL
        self._client = Groq(api_key=resolved_key)
        self._model = model

    def _complete_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2500,
    ) -> Dict[str, Any]:
        """Blocking call intended to run inside ``asyncio.to_thread``."""
        last_error: Exception | None = None
        response = None

        for attempt in range(self._MAX_RETRIES):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                break
            except (RateLimitError, APIConnectionError) as exc:
                last_error = exc
                if attempt == self._MAX_RETRIES - 1:
                    break
                sleep_time = self._BASE_BACKOFF_SECONDS * (2**attempt)
                time.sleep(sleep_time)
            except APIStatusError as exc:
                # 4xx (non-429) client errors will not be fixed by retrying.
                raise LLMReasoningError(f"Groq API rejected request ({exc.status_code}): {exc.message}") from exc
            except Exception as exc:
                raise LLMReasoningError(f"Unexpected error communicating with Groq: {exc}") from exc

        if response is None:
            raise LLMReasoningError(
                f"Groq request failed after {self._MAX_RETRIES} attempts. Last error: {last_error}"
            ) from last_error

        choice = response.choices[0] if response.choices else None
        raw_text = choice.message.content if choice and choice.message else None
        if not raw_text:
            raise LLMReasoningError("Groq returned an empty response body.")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise LLMReasoningError(f"Groq response was not valid JSON: {raw_text[:200]}") from exc

        if not isinstance(parsed, dict):
            raise LLMReasoningError(
                f"Groq response was JSON, but not an object (got {type(parsed).__name__}): {raw_text[:200]}"
            )

        # Attach raw token usage to the parsed dict under a private key so callers
        # can log it without polluting domain fields.
        usage = getattr(response, "usage", None)
        parsed["_usage"] = {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
            "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
            "total_tokens": getattr(usage, "total_tokens", 0) or 0,
        }
        return parsed

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2500,
    ) -> Dict[str, Any]:
        """Run one JSON-mode completion off the event loop.

        Raises :class:`LLMReasoningError` for every failure mode (auth,
        transient downtime, invalid JSON), giving calling agents a reliable,
        single exception type to catch for their fallback path.
        """
        try:
            return await asyncio.to_thread(
                self._complete_json_sync,
                system_prompt,
                user_prompt,
                max_tokens,
            )
        except LLMReasoningError:
            raise
        except Exception as exc:  # Defensive: never let a raw error escape.
            raise LLMReasoningError(f"Unexpected completion failure: {exc}") from exc


def build_token_log(node_name: str, usage: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert Groq usage stats into the graph's telemetry log shape."""
    in_tokens = int(usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0)
    out_tokens = int(usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0)
    cost = (in_tokens / 1_000_000 * COST_PER_MILLION_INPUT_TOKENS) + (
        out_tokens / 1_000_000 * COST_PER_MILLION_OUTPUT_TOKENS
    )
    return {
        "node": node_name,
        "input_tokens": in_tokens,
        "output_tokens": out_tokens,
        "estimated_cost": round(cost, 6),
    }
