"""
Conditional routing matrix for explicit multi-agent loop branches.

Routes expose the self-healing diagnostic gate and the terminal compliance
outcomes as simple, testable string labels.
"""

from src.graph.state import SharedState


def route_after_supervisor(state: SharedState) -> str:
    """Route approved diagnoses to compliance or retry unresolved diagnostics."""
    if (
        state.critic_feedback != "APPROVED_BY_SUPERVISOR"
        and state.retry_count <= 3
    ):
        print(
            "[ROUTER] Self-Healing loop triggered! Redirecting back to "
            f"Diagnostic Node (Retry: {state.retry_count}/3)"
        )
        return "diagnostic"
    print(
        "[ROUTER] Diagnostic output approved by Supervisor. Routing directly "
        "to Compliance Gate."
    )
    return "compliance"


def route_after_compliance(state: SharedState) -> str:
    """Route failed governance checks to end, otherwise continue to completion."""
    if "FAILED" in state.compliance_status:
        print(
            "[ROUTER] Compliance validation critical alert! Routing directly "
            "to final completion."
        )
        return "end"
    print(
        "[ROUTER] Governance criteria clean. Moving forward into user "
        "evaluation network."
    )
    return "continue"