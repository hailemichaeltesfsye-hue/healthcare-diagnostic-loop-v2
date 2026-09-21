"""Critic node: the missing piece of the self-healing diagnostic retry loop.

``src/graph/edges.py`` already contained ``route_after_supervisor``, which
reads ``state.critic_feedback`` to decide whether to loop back to the
diagnostic node. Nothing in the repository ever set that field, so the
routing function was dead code - it wasn't wired into ``compile_workflow()``
at all, and even if it had been, ``critic_feedback`` would never equal
``"APPROVED_BY_SUPERVISOR"``, which (depending on how it were wired) could
either never approve or never retry. This module is what actually evaluates
the diagnostic agent's confidence score and decides.
"""

from typing import Any, Dict

from src.graph.state import SharedState

# A path scoring at or above this on the diagnostic agent's own 0-10 scale is
# considered safe to proceed with. Below it, the critic asks for a retry.
CONFIDENCE_THRESHOLD = 7.0

# Matches the "(Retry: n/3)" cap already described in edges.py's log message
# and the repository's README. After this many retries, the critic approves
# the best available path rather than looping forever.
MAX_RETRIES = 3


async def critic_node(state: SharedState) -> Dict[str, Any]:
    """Gate the diagnostic agent's output on its own reported confidence.

    Runs after ``diagnostic`` and before ``compliance``. Sets
    ``critic_feedback`` to the sentinel ``"APPROVED_BY_SUPERVISOR"`` when the
    path is confident enough (or the retry budget is exhausted), which
    ``route_after_supervisor`` reads to send the case on to compliance.
    Otherwise it writes concrete, actionable feedback and increments
    ``retry_count`` so the diagnostic agent's next attempt can visibly
    account for it.
    """
    if state.retry_count >= MAX_RETRIES:
        print(
            f"[CRITIC] Retry budget exhausted ({state.retry_count}/{MAX_RETRIES}) at "
            f"confidence {state.diagnostic_confidence}/10 - approving the best "
            "available path rather than looping indefinitely."
        )
        return {
            "critic_feedback": "APPROVED_BY_SUPERVISOR",
            "current_step": "CRITIC_APPROVED_MAX_RETRIES",
        }

    if state.diagnostic_confidence >= CONFIDENCE_THRESHOLD:
        print(
            f"[CRITIC] Confidence {state.diagnostic_confidence}/10 meets the "
            f"{CONFIDENCE_THRESHOLD}/10 threshold - approved."
        )
        return {
            "critic_feedback": "APPROVED_BY_SUPERVISOR",
            "current_step": "CRITIC_APPROVED",
        }

    feedback = (
        f"Prior attempt scored {state.diagnostic_confidence}/10, below the "
        f"{CONFIDENCE_THRESHOLD}/10 safety threshold. Reconsider using the full "
        "symptom list and research context, prefer the safer/more conservative "
        "path when evidence is ambiguous, and be more specific than a generic "
        "wait-and-see recommendation if the symptoms warrant it."
    )
    print(
        f"[CRITIC] Confidence {state.diagnostic_confidence}/10 below threshold - "
        f"requesting retry {state.retry_count + 1}/{MAX_RETRIES}."
    )
    return {
        "critic_feedback": feedback,
        "retry_count": state.retry_count + 1,
        "current_step": "CRITIC_REQUESTED_RETRY",
    }
