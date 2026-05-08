from typing import List, Dict, Any
import json
from evaluation.judge_gpt import GPTJudge, FailureClassification
from evaluation.rubric_engine import RubricEngine

class Round4Judge:
    """
    Final Judge evaluates the entire debate history.
    """
    def __init__(self):
        self.gpt_judge = GPTJudge()
        self.rubric_engine = RubricEngine()

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
            # For each agent, judge their final Round 3 answer
            # We also pass the debate history (simplified)
            output = round3_res.get("response", "")
            
            # Calculate rubric score for Round 3
            rubric_score = self.rubric_engine.score_output("debate_task", agent_id, output, rubric)
            
            # Classify failure
            classification = self.gpt_judge.classify_failure(
                instruction,
                instruction_type,
                output,
                rubric_score,
                [] # We could pass the full debate history trace here
            )
            
            judgments[agent_id] = {
                "rubric_score": rubric_score,
                "failure_classification": classification
            }
            
        return {
            "judgments": judgments,
            "ground_truth_summary": "Summary of debate findings pending full implementation",
            "overall_reliability_score": 0
        }
