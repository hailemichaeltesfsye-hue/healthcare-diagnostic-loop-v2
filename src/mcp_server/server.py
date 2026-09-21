"""
Custom MCP protocol emulation pipeline.

Exposes standard interfaces for fetching clinical metadata safely inside
automated loops.
"""

import json
from typing import Any, Dict

from src.mcp_server.tools import MedicalKnowledgeBase


class MCPServerContext:
    """Orchestrate programmatic execution maps for verified MCP tool bindings."""

    def __init__(self) -> None:
        """Initialize the context with the internal medical knowledge base."""
        self.kb = MedicalKnowledgeBase()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a registered tool and return a JSON-encoded response.

        Invalid tool names and unexpected execution failures are converted to
        structured error responses so callers never need to parse exceptions as
        part of the normal tool protocol.
        """
        try:
            if tool_name == "fetch_medical_guidelines":
                target_conditions = arguments.get("conditions", [])
                result_data = self.kb.get_guidelines(target_conditions)
                return json.dumps(
                    {
                        "tool": "fetch_medical_guidelines",
                        "status": "SUCCESS",
                        "data": result_data,
                    }
                )

            if tool_name == "validate_drug_interactions":
                target_drugs = arguments.get("drugs", [])
                interaction_report = self.kb.check_interactions(target_drugs)
                return json.dumps(
                    {
                        "tool": "validate_drug_interactions",
                        "status": "SUCCESS",
                        "data": interaction_report,
                    }
                )

            return json.dumps(
                {
                    "status": "ERROR",
                    "message": f"Tool call validation failure: {tool_name} not registered.",
                }
            )
        except Exception as error:
            return json.dumps(
                {
                    "status": "CRITICAL_EXECUTION_FAULT",
                    "message": str(error),
                }
            )


print("Part 1 Core Architecture components successfully instantiated.")