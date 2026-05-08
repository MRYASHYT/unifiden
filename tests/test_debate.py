import pytest
from debate.debate_coordinator import DebateCoordinator
from debate.round_1_runner import Round1Runner
from debate.round_2_reviewer import Round2Reviewer
from debate.round_3_reviser import Round3Reviser
from agents.base_agent import BaseAgent, AgentResult, ToolCall

class MockAgent(BaseAgent):
    def __init__(self, aid):
        super().__init__(agent_id=aid, model="mock", temperature=0)
    
    def setup(self): pass
    
    def run(self, inst, inst_type):
        return AgentResult(self.agent_id, "mock", "mock", inst, inst_type, "output", [], 1, 1.0, True, None, 10, [], "run1", 0.0)
    
    def run_with_peer_context(self, inst, rnd, peer_data):
        return {"agent_id": self.agent_id, "round": rnd, "response": f"review from {self.agent_id}"}

def test_round1():
    agents = [MockAgent("a1"), MockAgent("a2")]
    r1 = Round1Runner(agents)
    res = r1.run("test", "clear")
    assert len(res) == 2
    assert "a1" in res

def test_round2():
    agents = [MockAgent("a1"), MockAgent("a2")]
    r2 = Round2Reviewer(agents)
    r1_res = {"a1": AgentResult("a1", "mock", "mock", "test", "clear", "out", [], 1, 1.0, True, None, 10, [], "run1", 0.0)}
    res = r2.run("test", r1_res)
    assert len(res) == 2

def test_round3():
    agents = [MockAgent("a1"), MockAgent("a2")]
    r3 = Round3Reviser(agents)
    r1_res = {"a1": AgentResult("a1", "mock", "mock", "test", "clear", "out", [], 1, 1.0, True, None, 10, [], "run1", 0.0),
              "a2": AgentResult("a2", "mock", "mock", "test", "clear", "out2", [], 1, 1.0, True, None, 10, [], "run2", 0.0)}
    r2_res = {"a1": {"agent_id": "a1", "response": "review"}, "a2": {"agent_id": "a2", "response": "review"}}
    res = r3.run("test", r1_res, r2_res)
    assert len(res) == 2
