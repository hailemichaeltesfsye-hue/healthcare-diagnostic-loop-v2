"""Typed supervisor coordinating the Part 2 diagnostic agent sequence."""

from typing import Any, Dict

from src.agents.diagnostic import DiagnosticAgent
from src.agents.researcher import ResearcherAgent
from src.agents.triage import TriageAgent
from src.graph.state import SharedState


class SupervisorAgent:
    """Run triage, research, and diagnostic nodes in a deterministic sequence."""

    def __init__(self) -> None:
        """Construct the agent nodes managed by this supervisor."""
        self.triage_agent = TriageAgent()
        self.researcher_agent = ResearcherAgent()
        self.diagnostic_agent = DiagnosticAgent()

    async def process(self, state: SharedState) -> SharedState:
        """
        Execute the complete Part 2 workflow and return the resulting state.

        Each node emits a partial update compatible with LangGraph state
        reducers. Applying updates through Pydantic preserves validation at every
        handoff and prevents accidental mutation of the original state object.
        """
        current_state = state.model_copy(deep=True)
        for agent in (
            self.triage_agent,
            self.researcher_agent,
            self.diagnostic_agent,
        ):
            update: Dict[str, Any] = await agent.process(current_state)
            current_state = current_state.model_copy(update=update, deep=True)
        current_state.current_step = "SUPERVISOR_COMPLETE"
        return current_state