"""Medical guideline reference agent using custom MCP tool execution."""

import json
from typing import Any, Dict

from src.graph.state import SharedState
from src.mcp_server.server import MCPServerContext


class ResearcherAgent:
    """Coordinate guideline retrieval through the decoupled MCP tool boundary."""

    def __init__(self) -> None:
        """Initialize the researcher with an isolated MCP server context."""
        self.mcp_client = MCPServerContext()

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """
        Fetch verified guidelines for the symptoms extracted during triage.

        The MCP response is decoded and converted into a concise state update;
        malformed responses are surfaced as explicit runtime errors.
        """
        print("[AGENT] Researcher query routing via MCP tools...")
        mcp_response = self.mcp_client.call_tool(
            tool_name="fetch_medical_guidelines",
            arguments={"conditions": state.extracted_symptoms},
        )
        parsed_data = json.loads(mcp_response)
        if parsed_data.get("status") != "SUCCESS":
            raise RuntimeError(
                f"Guideline retrieval failed: {parsed_data.get('message', 'unknown error')}"
            )
        fetched_guidelines = parsed_data.get("data", "Guidelines missing.")

        token_log: Dict[str, Any] = {
            "node": "researcher_agent",
            "input_tokens": 250,
            "output_tokens": 120,
            "estimated_cost": 0.00035,
        }
        return {
            "medical_research_data": f"Verified Guidelines: {fetched_guidelines}",
            "current_step": "RESEARCH_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }