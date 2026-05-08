import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai
import os

@dataclass
class RubricScore:
    task_id: str
    agent_id: str
    required_elements_present: List[str]
    required_elements_missing: List[str]
    forbidden_elements_found: List[str]
    raw_score: int
    max_score: int
    percentage: float
    grading_reasoning: str

class RubricEngine:
    """
    Upgraded Rubric Engine using LLM-based semantic grading.
    No longer relies on naive keyword matching.
    """
    
    def __init__(self, rubrics_path: str = "tasks/rubrics.json"):
        self.rubrics_path = rubrics_path
        self.rubrics = self._load_rubrics()
        # Initialize Gemini for grading
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

    def _load_rubrics(self) -> Dict[str, Any]:
        try:
            with open(self.rubrics_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def score_output(
        self, 
        task_id: str, 
        agent_id: str, 
        output: str, 
        rubric_data: Optional[Dict[str, Any]] = None
    ) -> RubricScore:
        rubric = rubric_data or self.rubrics.get(task_id)
        if not rubric:
            raise ValueError(f"Rubric for task {task_id} not found.")

        req = rubric.get("required_elements", [])
        forb = rubric.get("forbidden_elements", [])
        
        prompt = f"""
        You are a strict technical grader. Evaluate the agent's output based on the rubric.
        
        OUTPUT TO GRADE:
        {output}
        
        REQUIRED ELEMENTS: {req}
        FORBIDDEN ELEMENTS: {forb}
        
        Identify which required elements are SEMANTICALLY present and which are missing.
        Identify if any forbidden elements are present.
        
        Return JSON ONLY:
        {{
            "present": [list],
            "missing": [list],
            "forbidden_found": [list],
            "reasoning": "string"
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            clean_res = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_res)
        except:
            # Fallback to naive if LLM fails
            result = {"present": [], "missing": req, "forbidden_found": [], "reasoning": "LLM Grading Error"}

        present = result.get("present", [])
        missing = result.get("missing", [])
        forbidden_found = result.get("forbidden_found", [])
        
        raw_score = len(present) - (len(forbidden_found) * 2)
        max_score = len(req)
        percentage = (max(0, raw_score) / max_score * 100) if max_score > 0 else 0.0
        
        return RubricScore(
            task_id=task_id,
            agent_id=agent_id,
            required_elements_present=present,
            required_elements_missing=missing,
            forbidden_elements_found=forbidden_found,
            raw_score=raw_score,
            max_score=max_score,
            percentage=percentage,
            grading_reasoning=result.get("reasoning", "")
        )
