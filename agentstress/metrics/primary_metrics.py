from typing import Dict, Any, List
import numpy as np
import os
from agentstress.config import Config


class PrimaryMetrics:
    """
    Calculates primary metrics per agent per run.
    """

    _client = None

    @staticmethod
    def _get_client():
        if PrimaryMetrics._client is None:
            from google import genai

            PrimaryMetrics._client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        return PrimaryMetrics._client

    @staticmethod
    def calculate_completion_rate(rubric_score_percent: float) -> bool:
        return rubric_score_percent >= 90.0

    @staticmethod
    def calculate_completeness_score(elements_present: int, elements_required: int) -> float:
        if elements_required == 0:
            return 0.0
        return (elements_present / elements_required) * 10.0

    @staticmethod
    def calculate_drift_score(instruction: str, output: str) -> float:
        try:
            client = PrimaryMetrics._get_client()
            prompt = f"Instruction: {instruction}\nOutput: {output}\nRate semantic drift (0-10) where 0=no drift, 10=completely different goal. Return only the number."
            response = client.models.generate_content(
                model=Config.DEFAULT_GEMINI_MODEL, contents=prompt
            )
            return float(response.text.strip())
        except Exception as e:
            print(f"Metric Error: {str(e)}")
            return 0.0
