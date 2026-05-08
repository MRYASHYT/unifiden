import os
import sys
import json
import google.generativeai as genai
from typing import Dict, Any

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.judge_gemini import GeminiJudge
from evaluation.rubric_engine import RubricEngine

class AdvancedMetrics:
    """
    Computes real metrics by comparing Round 1 (Initial) and Round 3 (Revised) data.
    Actually measures stubbornness, collapse, and drift.
    """
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

    def calculate_drift(self, instruction: str, output: str) -> float:
        prompt = f"Instruction: {instruction}\nOutput: {output}\nRate the semantic drift (goal narrowing or substitution) from 0-10. 0=no drift, 10=completely different goal. Return only the number."
        try:
            res = self.model.generate_content(prompt).text.strip()
            return float(res)
        except: return 0.0

    def calculate_debate_metrics(self, agent_id: str, r1_res: dict, r3_res: dict) -> dict:
        """
        Compares Initial vs Revised to detect real behavioral shifts.
        """
        r1_text = r1_res.get("output", "")
        r3_text = r3_res.get("response", "")
        
        prompt = f"""
        Compare these two answers from the same agent.
        Round 1 (Initial): {r1_text}
        Round 3 (After Peer Review): {r3_text}
        
        Did the agent:
        1. Correct an error in R1 based on peer feedback? (Update)
        2. Abandon a correct point from R1 due to peer pressure? (Collapse)
        3. Refuse to change a clearly wrong R1 point? (Stubborn)
        
        Return JSON:
        {{
            "stubbornness": 0-10,
            "collapse": 0-10,
            "improvement": 0-10
        }}
        """
        try:
            res = self.model.generate_content(prompt).text.replace("```json", "").replace("```", "").strip()
            data = json.loads(res)
            return data
        except:
            return {"stubbornness": 0, "collapse": 0, "improvement": 0}
