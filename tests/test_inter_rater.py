import pytest
from agentstress.evaluation.inter_rater import InterRater

def test_perfect_agreement():
    j1 = ["NO_FAILURE", "INSTRUCTION_DRIFT"]
    j2 = ["NO_FAILURE", "INSTRUCTION_DRIFT"]
    assert InterRater.calculate_cohens_kappa(j1, j2) == 1.0

def test_zero_agreement():
    j1 = ["NO_FAILURE", "INSTRUCTION_DRIFT"]
    j2 = ["PARTIAL_FAILURE", "TOOL_CALL_HALLUCINATION"]
    assert InterRater.calculate_cohens_kappa(j1, j2) == 0.0

def test_partial_agreement():
    j1 = ["NO_FAILURE", "INSTRUCTION_DRIFT", "NO_FAILURE", "TOOL_CALL_HALLUCINATION"]
    j2 = ["NO_FAILURE", "INSTRUCTION_DRIFT", "PARTIAL_FAILURE", "TOOL_CALL_HALLUCINATION"]
    kappa = InterRater.calculate_cohens_kappa(j1, j2)
    assert 0.5 < kappa < 1.0

def test_empty_lists():
    assert InterRater.calculate_cohens_kappa([], []) == 0.0
    assert InterRater.calculate_cohens_kappa(["NO_FAILURE"], []) == 0.0
