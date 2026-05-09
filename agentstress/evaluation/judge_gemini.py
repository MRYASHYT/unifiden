import json
from typing import List, Dict, Any, Optional
from google import genai
import os
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from agentstress.config import Config
from agentstress.evaluation.rubric_engine import RubricScore, RubricEngine
from agentstress.evaluation.base_judge import BaseJudge, FailureClassification, DebateJudgment
from agentstress import logger


class GeminiJudge(BaseJudge):
    """
    Judge using Gemini 1.5 for cost-effective evaluation.
    Uses the modern google-genai SDK for consistency with the rest of the framework.
    """

    def __init__(self, model: str = None):
        self.model_name = model or Config.DEFAULT_GEMINI_MODEL
        self.client = None
        self.rubric_engine = RubricEngine()

    def _setup_client(self):
        if self.client is None:
            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def score_rubric(
        self, task_id: str, instruction: str, agent_output: str, rubric: dict
    ) -> RubricScore:
        return self.rubric_engine.score_output(task_id, "GEMINI_JUDGE", agent_output, rubric)

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]],
    ) -> FailureClassification:
        self._setup_client()
        prompt = f"""
        Classify the failure mode of the following AI agent output.
        TASK: {instruction}
        TYPE: {instruction_type}
        AGENT_OUTPUT: {agent_output}
        RUBRIC_SCORE: {rubric_score.percentage}%
        
        Available failure modes:
        - NO_FAILURE
        - INSTRUCTION_DRIFT
        - PREMATURE_TERMINATION
        - TOOL_CALL_HALLUCINATION
        - OVERCONFIDENCE_COLLAPSE
        - STUBBORNNESS_FAILURE
        - CONTAMINATION
        
        Return JSON ONLY:
        {{
            "failure_mode": "string",
            "confidence": int (0-10),
            "reasoning": "string"
        }}
        """
        try:

            @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
            def invoke_model():
                return self.client.models.generate_content(model=self.model_name, contents=prompt)

            res = invoke_model()
            text = res.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text)
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode=data.get("failure_mode", "UNKNOWN"),
                confidence=data.get("confidence", 0),
                evidence="N/A",
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning=data.get("reasoning", ""),
            )
        except Exception as e:
            logger.error(f"CLASSIFICATION ERROR: {str(e)}")
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode="ERROR",
                confidence=0,
                evidence=str(e),
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning=f"Failed to classify: {str(e)}",
            )

    def judge_debate(
        self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict
    ) -> DebateJudgment:
        return DebateJudgment(
            task=task,
            instruction_type="N/A",
            ground_truth="Scaffolded",
            agent_scores={},
            hallucination_propagation={},
            reliability_ranking=[],
            production_recommendation="N/A",
            framework_insights=[],
            overall_reliability_score=0,
            experiment_metadata={},
        )
