"""Peer-to-peer adapters for the diagnostic workforce StateGraph."""

from typing import Any, Dict

from src.agents.compliance import ComplianceAgent
from src.agents.critic import critic_node
from src.agents.diagnostic import DiagnosticAgent
from src.agents.researcher import ResearcherAgent
from src.agents.triage import TriageAgent
from src.graph.state import SharedState

__all__ = [
    "triage_node",
    "researcher_node",
    "diagnostic_node",
    "critic_node",
    "compliance_node",
    "hitl_node",
    "final_compile_node",
]


triage_worker = TriageAgent()
researcher_worker = ResearcherAgent()
diagnostic_worker = DiagnosticAgent()
compliance_worker = ComplianceAgent()


async def triage_node(state: SharedState) -> Dict[str, Any]:
    """Execute triage and return its validated partial state update."""
    return await triage_worker.process(state)


async def researcher_node(state: SharedState) -> Dict[str, Any]:
    """Execute medical research and return its validated partial state update."""
    return await researcher_worker.process(state)


async def diagnostic_node(state: SharedState) -> Dict[str, Any]:
    """Execute diagnostic reasoning and return its partial state update."""
    return await diagnostic_worker.process(state)


async def compliance_node(state: SharedState) -> Dict[str, Any]:
    """Execute compliance auditing and return its partial state update."""
    return await compliance_worker.process(state)


async def hitl_node(state: SharedState) -> Dict[str, Any]:
    """
    Represent the human checkpoint without introducing a central supervisor.

    A caller supplies ``hitl_approved=True`` when a practitioner approves the
    report. Until then, the node leaves the workflow in an explicit pending
    state; a subsequent run can resume the same peer path with approval.
    """
    if "FAILED" in state.compliance_status:
        return {
            "hitl_approved": False,
            "current_step": "HITL_BLOCKED_BY_COMPLIANCE",
        }
    if state.hitl_approved is True:
        return {"current_step": "HITL_APPROVED"}
    return {"hitl_approved": None, "current_step": "HITL_PENDING"}


async def final_compile_node(state: SharedState) -> Dict[str, Any]:
    """Finalize the workflow status after compliance and HITL approval.

    Deliberately does NOT overwrite ``final_clinical_report`` with hardcoded
    English text: the compliance agent already composed that report directly
    in the patient's detected language (including the halt/pending message
    when compliance failed or HITL hasn't approved yet). Mixing in English
    boilerplate here would make the downstream gTTS voice_output_node read a
    hybrid of two languages. Status is communicated via ``current_step``
    instead, which the dashboard already surfaces separately.
    """
    if "FAILED" in state.compliance_status:
        return {"current_step": "FINAL_COMPILATION_BLOCKED"}
    if state.hitl_approved is not True:
        return {"current_step": "FINAL_COMPILATION_PENDING_HITL"}
    return {"current_step": "FINAL_COMPILATION_COMPLETE"}