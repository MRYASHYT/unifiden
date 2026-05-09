import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.evaluation.judge_gpt import GPTJudge
from agentstress.evaluation.base_judge import FailureClassification


def test_judge_initialization():
    judge = GPTJudge()
    assert judge.model == "gpt-4o"


def test_failure_classification_dataclass():
    fc = FailureClassification(
        agent_id="a1",
        failure_mode="NO_FAILURE",
        confidence=10,
        evidence="none",
        drift_score=0,
        completeness_score=10,
        hallucination_detected=False,
        hallucination_content=None,
        reasoning="test",
    )
    assert fc.failure_mode == "NO_FAILURE"
