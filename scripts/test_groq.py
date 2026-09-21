"""Make one authenticated Groq API request to verify local configuration."""

import os
import sys

from dotenv import load_dotenv
from groq import Groq


DEFAULT_MODEL = "openai/gpt-oss-120b"


def main() -> int:
    """Load configuration, call Groq once, and print the returned response."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_actual_key_here":
        print(
            "GROQ_API_KEY is not configured. Add your raw key to .env and rerun "
            "this script."
        )
        return 1

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Groq API integration verified.",
            }
        ],
        temperature=0,
        max_tokens=256,
    )
    choice = response.choices[0]
    message = choice.message.content or getattr(choice.message, "reasoning_content", "")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Response: {message}")
    print(f"Finish reason: {choice.finish_reason}")
    if response.usage is not None:
        print(
            "Usage: "
            f"prompt_tokens={response.usage.prompt_tokens}, "
            f"completion_tokens={response.usage.completion_tokens}, "
            f"total_tokens={response.usage.total_tokens}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())