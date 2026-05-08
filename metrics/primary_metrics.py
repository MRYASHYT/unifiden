from typing import Dict, Any, List
import numpy as np

class PrimaryMetrics:
    """
    Calculates primary metrics per agent per run.
    """
    @staticmethod
    def calculate_completion_rate(rubric_score_percent: float) -> bool:
        return rubric_score_percent >= 90.0

    @staticmethod
    def calculate_completeness_score(elements_present: int, elements_required: int) -> float:
        if elements_required == 0: return 0.0
        return (elements_present / elements_required) * 10.0

    @staticmethod
    def calculate_drift_score(instruction: str, output: str) -> float:
        # Simplified: In full version, use an LLM to evaluate semantic drift
        return 0.0 
