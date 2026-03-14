from unittest.mock import patch

from model_tools import get_tool_definitions
from run_agent import AIAgent


def test_get_tool_definitions_includes_smart_model_when_enabled():
    tools = get_tool_definitions(enabled_toolsets=["smart_model"], quiet_mode=True)
    names = {tool["function"]["name"] for tool in tools}
    assert "smart_model" in names


def test_aiagent_exposes_smart_model_in_valid_tool_names():
    with patch("run_agent.OpenAI"):
        agent = AIAgent(
            api_key="test-k...7890",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
        )
    assert "smart_model" in agent.valid_tool_names
