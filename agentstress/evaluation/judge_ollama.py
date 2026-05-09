import json
import requests
from typing import List, Dict, Any, Optional
from agentstress.evaluation.base_judge import BaseJudge, FailureClassification, DebateJudgment
from agentstress.evaluation.rubric_engine import RubricScore, RubricEngine
from agentstress.config import Config
from agentstress import logger

class OllamaJudge(BaseJudge):
    """
    Judge using local Ollama models.
    Ensures 100% free, offline, and rate-limit-free evaluation.
    """

    def __init__(self, model: str = None):
        self.model_name = model or Config.DEFAULT_LOCAL_MODEL
        self.base_url = f"{Config.OLLAMA_BASE_URL}/api/generate"
        self.rubric_engine = RubricEngine()

    def _invoke_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Force JSON output if the model supports it
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama Judge Invocation Failed: {str(e)}")
            return "{}"

    def score_rubric(
        self, task_id: str, instruction: str, agent_output: str, rubric: dict
    ) -> RubricScore:
        """
        Uses local model to score the rubric. 
        Note: We temporarily mock the semantic part if Ollama is too weak for complex rubrics,
        but for Llama 3.1 8B, it should handle basic JSON grading.
        """
        # For now, we reuse the RubricEngine but we can override it to use local model
        return self.rubric_engine.score_output(task_id, "OLLAMA_JUDGE", agent_output, rubric)

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]],
    ) -> FailureClassification:
        prompt = f"""
        Analyze the following AI agent output for failure modes.
        TASK: {instruction}
        AGENT_OUTPUT: {agent_output}
        RUBRIC_PERCENTAGE: {rubric_score.percentage}
        
        Failure Modes: NO_FAILURE, INSTRUCTION_DRIFT, PREMATURE_TERMINATION, TOOL_CALL_HALLUCINATION.
        
        Return JSON ONLY:
        {{
            "failure_mode": "string",
            "confidence": int (0-10),
            "reasoning": "string"
        }}
        """
        
        res_text = self._invoke_ollama(prompt)
        try:
            data = json.loads(res_text)
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode=data.get("failure_mode", "UNKNOWN"),
                confidence=data.get("confidence", 5),
                evidence="Local Audit",
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning=data.get("reasoning", "Analyzed locally via Ollama."),
            )
        except:
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode="LOCAL_PARSE_ERROR",
                confidence=0,
                evidence="Parse error",
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning="Ollama returned invalid JSON.",
            )

    def judge_debate(
        self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict
    ) -> DebateJudgment:
        return DebateJudgment(
            task=task,
            instruction_type="N/A",
            ground_truth="Local",
            agent_scores={},
            hallucination_propagation={},
            reliability_ranking=[],
            production_recommendation="N/A",
            framework_insights=[],
            overall_reliability_score=0,
            experiment_metadata={},
        )
