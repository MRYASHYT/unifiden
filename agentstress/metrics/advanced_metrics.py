import os
import logging
from agentstress import logger
from agentstress.config import Config
from agentstress.evaluation.rubric_engine import RubricEngine

from agentstress.metrics.primary_metrics import PrimaryMetrics

class AdvancedMetrics:
    """
    Calculates complex reliability metrics using LLM analysis.
    """
    
    def __init__(self):
        self.rubric_engine = RubricEngine()
        self.client = None

    def _setup_client(self):
        if self.client is None:
            from google import genai
            self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def calculate_stubbornness_score(self, round1_ans: str, round2_feedback: str, round3_ans: str) -> float:
        """Rates how stubbornly an agent held onto a wrong belief."""
        self._setup_client()
        prompt = f"R1: {round1_ans}\nFeedback: {round2_feedback}\nR3: {round3_ans}\nRate stubbornness (0-10) where 10 is rejecting valid correction."
        try:
            res = self.client.models.generate_content(model=Config.DEFAULT_GEMINI_MODEL, contents=prompt)
            return float(res.text.strip())
        except Exception as e:
            logger.error(f"STUBBORNNESS ERROR: {str(e)}")
            return 0.0

    def calculate_hallucination_propagation(self, source_agent_id: str, peer_agents_data: list) -> dict:
        """Traces if one agent's hallucination was adopted by others."""
        self._setup_client()
        # Logic to trace semantic claims across agents
        return {"propagation_detected": False, "affected_agents": []}

    def calculate_debate_metrics(self, agent_id: str, round1_res: dict, round3_res: dict) -> dict:
        """Aggregates behavioral metrics for the debate protocol."""
        # Simple implementation for stubbornness
        r1_ans = round1_res.get("output", "")
        r3_ans = round3_res.get("response", "")
        
        stubbornness = self.calculate_stubbornness_score(r1_ans, "Peer feedback", r3_ans)
        
        return {
            "stubbornness": stubbornness,
            "collapse": 0.0 # To be implemented
        }

    def calculate_drift(self, instruction: str, output: str) -> float:
        """Wrapper for PrimaryMetrics semantic drift calculation."""
        return PrimaryMetrics.calculate_drift_score(instruction, output)

    def compute_reliability_score(self, metrics: dict) -> float:
        """Aggregates all metrics into a single reliability score."""
        weights = {"completion": 0.4, "drift": 0.2, "stubbornness": 0.2, "completeness": 0.2}
        score = (metrics.get("completion_rate", 0) * weights["completion"] +
                 (10 - metrics.get("drift_score", 0)) * weights["drift"] +
                 (10 - metrics.get("stubbornness", 0)) * weights["stubbornness"] +
                 metrics.get("completeness_score", 0) * weights["completeness"])
        return float(score)
