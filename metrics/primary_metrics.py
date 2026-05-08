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
        import google.generativeai as genai
        import os
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel('models/gemini-flash-latest')
            prompt = f"Instruction: {instruction}\nOutput: {output}\nRate semantic drift (0-10) where 0=no drift, 10=completely different goal. Return only the number."
            return float(model.generate_content(prompt).text.strip())
        except Exception as e: return 0.0
