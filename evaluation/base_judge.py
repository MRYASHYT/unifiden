from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from evaluation.rubric_engine import RubricScore
from evaluation.judge_gpt import FailureClassification

@dataclass
class DebateJudgment:
    task: str
    instruction_type: str
    ground_truth: str
    agent_scores: dict
    hallucination_propagation: dict
    reliability_ranking: List[dict]
    production_recommendation: str
    framework_insights: List[str]
    overall_reliability_score: int
    experiment_metadata: dict

class BaseJudge(ABC):
    @abstractmethod
    def score_rubric(self, task_id: str, instruction: str, agent_output: str, rubric: dict) -> RubricScore:
        pass
    
    @abstractmethod
    def classify_failure(self, instruction: str, instruction_type: str, agent_output: str, rubric_score: RubricScore, execution_trace: list) -> FailureClassification:
        pass
    
    @abstractmethod
    def judge_debate(self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict) -> DebateJudgment:
        pass
    
    def calculate_inter_rater_agreement(self, judge_1_scores: List[RubricScore], judge_2_scores: List[RubricScore]) -> float:
        agreements = sum(
            1 for s1, s2 in zip(judge_1_scores, judge_2_scores)
            if s1.failure_mode == s2.failure_mode
        )
        return agreements / len(judge_1_scores) if judge_1_scores else 0.0
