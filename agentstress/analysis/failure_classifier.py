from agentstress.evaluation.rubric_engine import RubricScore
from agentstress.evaluation.judge_gpt import FailureClassification
from agentstress.metrics.advanced_metrics import AdvancedMetrics


class FailureClassifier:
    """
    Final Failure Mode Assignment combining Rubric, Judge, and Behavioral Metrics.
    """

    @staticmethod
    def assign_failure_mode(
        rubric_score: RubricScore, behavioral_metrics: dict, drift_score: float
    ) -> str:
        if rubric_score.percentage >= 90.0:
            if behavioral_metrics.get("collapse", 0) > 7:
                return "OVERCONFIDENCE_COLLAPSE"
            return "NO_FAILURE"

        if drift_score > 7:
            return "INSTRUCTION_DRIFT"

        if rubric_score.percentage < 50.0:
            return "PREMATURE_TERMINATION"

        if behavioral_metrics.get("stubbornness", 0) > 7:
            return "STUBBORN_FAILURE"

        if len(rubric_score.forbidden_elements_found) > 0:
            return "TOOL_CALL_HALLUCINATION"

        return "PARTIAL_FAILURE"
