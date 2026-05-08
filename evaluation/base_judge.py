from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from evaluation.rubric_engine import RubricScore

@dataclass
class FailureClassification:
    agent_id: str
    failure_mode: str              # From taxonomy
    confidence: int                # 0-10
    evidence: str                  # Specific quote proving classification
    drift_score: int               # 0-10
    completeness_score: int        # 0-10
    hallucination_detected: bool
    hallucination_content: Optional[str]
    reasoning: str

@dataclass
class DebateJudgment:
    task: str
    instruction_type: str
    ground_truth: str
    agent_scores: dict             # agent_id -> scores
    hallucination_propagation: dict
    reliability_ranking: List[dict]
    production_recommendation: str
    framework_insights: List[str]
    overall_reliability_score: int
    experiment_metadata: dict

class BaseJudge(ABC):
    
    @abstractmethod
    def score_rubric(
        self,
        task_id: str,
        instruction: str,
        agent_output: str,
        rubric: dict
    ) -> RubricScore:
        pass
    
    @abstractmethod
    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: list
    ) -> FailureClassification:
        pass
    
    @abstractmethod
    def judge_debate(
        self,
        task: str,
        round_1_answers: dict,
        round_2_reviews: dict,
        round_3_answers: dict
    ) -> DebateJudgment:
        pass
    
    def calculate_inter_rater_agreement(
        self,
        judge_1_scores: List[RubricScore],
        judge_2_scores: List[RubricScore]
    ) -> float:
        """Agreement calculation between two judges"""
        # categorical agreement on failure mode
        if not judge_1_scores or len(judge_1_scores) != len(judge_2_scores):
            return 0.0
        agreements = sum(1 for s1, s2 in zip(judge_1_scores, judge_2_scores) if s1.percentage == s2.percentage)
        return agreements / len(judge_1_scores)
