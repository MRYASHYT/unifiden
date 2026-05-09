import pytest
import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.agents.base_agent import BaseAgent, AgentResult
from agentstress.evaluation.base_judge import (
    BaseJudge,
    RubricScore,
    FailureClassification,
    DebateJudgment,
)
from agentstress.data.local_ledger import LocalLedger


class MockAgent(BaseAgent):
    def __init__(self):
        super().__init__("mock", "mock", 0.0)

    def setup(self):
        pass

    def run(self, i, t):
        return AgentResult(
            "mock", "mock", "mock", i, t, "out", [], 0, 0, True, None, 10, [], "1", 0
        )

    def run_with_peer_context(self, i, r, p):
        return {}


class MockJudge(BaseJudge):
    def score_rubric(self, t, i, a, r):
        return RubricScore(t, "mock", [], [], [], 10, 10, 100.0, "")

    def classify_failure(self, i, it, a, r, e):
        return FailureClassification("mock", "NO_FAILURE", 10, "", 0, 10, False, None, "")

    def judge_debate(self, t, r1, r2, r3):
        return DebateJudgment(t, "", "", {}, {}, [], "", [], 100, {})


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


def test_ledger_does_not_mutate_input():
    ledger_path = "tests/temp_ledger.jsonl"
    ledger = LocalLedger(ledger_path)
    result_data = {"test": "data"}

    ledger.record_entry(result_data)

    assert result_data == {"test": "data"}
    assert ledger.verify_ledger()

    if os.path.exists(ledger_path):
        os.remove(ledger_path)


def test_ledger_verifies_legacy_signed_entries():
    ledger_path = "tests/temp_ledger.jsonl"
    ledger = LocalLedger(ledger_path)
    data = {"test": "legacy"}
    entry = {
        "timestamp": time.time(),
        "data": data,
        "signature": ledger.signer.sign_data(data),
        "public_key_path": ledger.signer.public_key_path,
    }

    with open(ledger_path, "w") as f:
        f.write(json.dumps(entry) + "\n")

    assert ledger.verify_ledger()

    if os.path.exists(ledger_path):
        os.remove(ledger_path)
