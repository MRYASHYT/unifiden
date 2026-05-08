import json
import dataclasses
from typing import List, Dict, Any
from evaluation.judge_gpt import GPTJudge, FailureClassification
from evaluation.rubric_engine import RubricEngine
from metrics.advanced_metrics import AdvancedMetrics

class Round4Judge:
    """
    Final Judge evaluates the entire debate history.
    Uses LLM-based semantic grading and behavioral metrics.
    """
    def __init__(self):
        self.gpt_judge = GPTJudge()
        self.rubric_engine = RubricEngine()
        self.adv_metrics = AdvancedMetrics()

    def run(
        self, 
        instruction: str, 
        instruction_type: str, 
        round1_results: dict, 
        round2_results: dict, 
        round3_results: dict,
        rubric: dict
    ) -> dict:
        print("  Evaluating debate outcomes...")
        
        judgments = {}
        for agent_id, round3_res in round3_results.items():
            r1_obj = round1_results[agent_id]
            # Convert to dict if it's a dataclass
            r1_res = dataclasses.asdict(r1_obj) if dataclasses.is_dataclass(r1_obj) else r1_obj
            
            output = round3_res.get("response", "")
            
            # 1. Semantic Rubric Score
            rubric_score = self.rubric_engine.score_output("debate_task", agent_id, output, rubric)
            
            # 2. Behavioral Metrics (Stubbornness, Collapse)
            debate_metrics = self.adv_metrics.calculate_debate_metrics(agent_id, r1_res, round3_res)
            
            # 3. Drift Analysis
            drift_score = self.adv_metrics.calculate_drift(instruction, output)
            
            # 4. Final Failure Classification
            classification = self.gpt_judge.classify_failure(
                instruction,
                instruction_type,
                output,
                rubric_score,
                [] # Can pass full trace in future iterations
            )
            
            judgments[agent_id] = {
                "rubric_score": rubric_score,
                "failure_classification": classification,
                "behavioral_metrics": debate_metrics,
                "drift_score": drift_score
            }
            
        return {
            "judgments": judgments,
            "overall_reliability_score": sum([j["rubric_score"].percentage for j in judgments.values()]) / len(judgments)
        }
