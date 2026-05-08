import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.agents.react_gpt import ReActGPTAgent
from agentstress.agents.reflexion_gpt import ReflexionGPTAgent

def test_agent_initialization():
    agent = ReActGPTAgent()
    assert agent.agent_id == "agent_1_react_gpt4o"
    assert agent.model == "gpt-4o"

def test_agent_result_structure():
    # Mock result to test validation
    from agentstress.agents.base_agent import AgentResult
    res = AgentResult(
        agent_id="test", architecture="test", model="test", instruction="test", 
        instruction_type="test", output="test", tool_calls=[], completed=True, run_id="1"
    )
    agent = ReActGPTAgent()
    assert agent.validate_result(res) == True

def test_reflexion_initialization():
    agent = ReflexionGPTAgent()
    assert "reflexion" in agent.agent_id
