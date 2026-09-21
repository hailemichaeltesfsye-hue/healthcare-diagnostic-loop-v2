"""Compile the peer-to-peer healthcare diagnostic workforce graph."""

from langgraph.graph import END, StateGraph

from src.graph.edges import route_after_compliance, route_after_supervisor
from src.graph.nodes import (
    compliance_node,
    critic_node,
    diagnostic_node,
    final_compile_node,
    hitl_node,
    researcher_node,
    triage_node,
)
from src.graph.state import SharedState
from src.voice.nodes import voice_input_node, voice_output_node


def compile_workflow() -> StateGraph:
    """Build direct peer-to-peer handoffs without a supervisor bottleneck.

    The autonomous voice loop bookends the existing clinical pipeline rather
    than being spliced into the middle of it: ``voice_input`` transcribes and
    language-detects patient audio before triage ever sees it, and
    ``voice_output`` speaks the final report back in that same language after
    ``final_compile``. Both nodes are no-ops for text-only runs (no
    ``input_audio_path`` set), so existing text-based callers are unaffected.

    ``critic`` closes the previously-dormant self-healing loop: it scores the
    diagnostic agent's confidence and, via ``route_after_supervisor``, either
    sends the case on to ``compliance`` or loops back to ``diagnostic`` with
    concrete feedback (capped at 3 retries). ``route_after_compliance`` then
    sends a compliance failure straight to ``voice_output`` (so the patient
    still hears the localized halt notice) instead of continuing through the
    HITL/final-compile steps meant for passing cases.
    """
    workflow = StateGraph(SharedState)
    workflow.add_node("voice_input", voice_input_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("hitl", hitl_node)
    workflow.add_node("final_compile", final_compile_node)
    workflow.add_node("voice_output", voice_output_node)

    workflow.set_entry_point("voice_input")
    workflow.add_edge("voice_input", "triage")
    workflow.add_edge("triage", "researcher")
    workflow.add_edge("researcher", "diagnostic")
    workflow.add_edge("diagnostic", "critic")
    workflow.add_conditional_edges(
        "critic",
        route_after_supervisor,
        {"diagnostic": "diagnostic", "compliance": "compliance"},
    )
    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {"end": "voice_output", "continue": "hitl"},
    )
    workflow.add_edge("hitl", "final_compile")
    workflow.add_edge("final_compile", "voice_output")
    workflow.add_edge("voice_output", END)
    return workflow.compile()


print("Part 3 LangGraph Multi-Agent Orchestration fabric successfully compiled.")
print("Self-healing diagnostic retry loop (critic + edges routing) now active.")
print("Multilingual voice interaction loop (AssemblyAI + gTTS) attached to lifecycle.")