import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentResult
from evaluation.base_judge import BaseJudge, RubricScore, FailureClassification, DebateJudgment
from data.local_ledger import LocalLedger

class MockAgent(BaseAgent):
    def __init__(self):
        super().__init__("mock", "mock", 0.0)
    def setup(self): pass
    def run(self, i, t): return AgentResult("mock", "mock", "mock", i, t, "out", [], 0, 0, True, None, 10, [], "1", 0)
    def run_with_peer_context(self, i, r, p): return {}

class MockJudge(BaseJudge):
    def score_rubric(self, t, i, a, r): return RubricScore(t, "mock", [], [], [], 10, 10, 100.0, "")
    def classify_failure(self, i, it, a, r, e): return FailureClassification("mock", "NO_FAILURE", 10, "", 0, 10, False, None, "")
    def judge_debate(self, t, r1, r2, r3): return DebateJudgment(t, "", "", {}, {}, [], "", [], 100, {})

def test_integration_pipeline():
    agent = MockAgent()
    judge = MockJudge()
    ledger = LocalLedger("tests/temp_ledger.jsonl")
    
    res = agent.run("test", "clear")
    assert res.completed
    
    score = judge.score_rubric("t1", "test", res.output, {})
    assert score.percentage == 100.0
    
    cls = judge.classify_failure("test", "clear", res.output, score, [])
    assert cls.failure_mode == "NO_FAILURE"
    
    sig = ledger.record_entry({"test": "data"})
    assert sig is not None
    assert ledger.verify_ledger()
    
    if os.path.exists("tests/temp_ledger.jsonl"):
        os.remove("tests/temp_ledger.jsonl")
