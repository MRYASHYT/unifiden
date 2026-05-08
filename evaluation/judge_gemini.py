import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
from evaluation.rubric_engine import RubricScore, RubricEngine
from evaluation.base_judge import BaseJudge, FailureClassification, DebateJudgment

class GeminiJudge(BaseJudge):
    """
    Judge using Gemini 1.5 for cost-effective evaluation.
    """
    
    def __init__(self, model: str = "models/gemini-flash-latest"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)
        self.rubric_engine = RubricEngine()

    def score_rubric(self, task_id: str, instruction: str, agent_output: str, rubric: dict) -> RubricScore:
        return self.rubric_engine.score_output(task_id, "GEMINI_JUDGE", agent_output, rubric)

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]]
    ) -> FailureClassification:
        prompt = f"Classify failure for task: {instruction}\nOutput: {agent_output}\nReturn JSON with failure_mode, confidence, reasoning."
        res = self.model.generate_content(prompt).text
        try:
            if "```json" in res: res = res.split("```json")[1].split("```")[0].strip()
            data = json.loads(res)
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode=data.get("failure_mode", "UNKNOWN"),
                confidence=data.get("confidence", 0),
                evidence="N/A", drift_score=0, completeness_score=0,
                hallucination_detected=False, hallucination_content=None, reasoning=data.get("reasoning", "")
            )
        except:
            return FailureClassification(
                agent_id=rubric_score.agent_id, failure_mode="ERROR", confidence=0,
                evidence="N/A", drift_score=0, completeness_score=0,
                hallucination_detected=False, hallucination_content=None, reasoning="Failed to parse"
            )

    def judge_debate(self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict) -> DebateJudgment:
        return DebateJudgment(
            task=task, instruction_type="N/A", ground_truth="Scaffolded", agent_scores={},
            hallucination_propagation={}, reliability_ranking=[], production_recommendation="N/A",
            framework_insights=[], overall_reliability_score=0, experiment_metadata={}
        )
