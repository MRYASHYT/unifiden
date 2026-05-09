import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import logging
from agentstress.config import Config
from agentstress import logger

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

    def __init__(self, rubrics_path: str = None):
        self.rubrics_path = rubrics_path or os.path.join(Config.TASKS_DIR, "rubrics.json")
        self.rubrics = self._load_rubrics()
        self.client = None

    def _setup_gemini(self):
        if self.client is None:
            try:
                from google import genai
                # The modern SDK handles versioning internally.
                self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {str(e)}")

    def _load_rubrics(self) -> Dict[str, Any]:
        try:
            with open(self.rubrics_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def score_output(
        self, task_id: str, agent_id: str, output: str, rubric_data: Optional[Dict[str, Any]] = None
    ) -> RubricScore:
        self._setup_gemini()
        rubric = rubric_data or self.rubrics.get(task_id)
        if not rubric:
            raise ValueError(f"Rubric for task {task_id} not found.")

        req = rubric.get("required_elements", [])
        forb = rubric.get("forbidden_elements", [])

        prompt = f"""
        [SYSTEM: INDUSTRIAL GRADER]
        Evaluate the following agent response.
        
        TASK: {task_id}
        RESPONSE: {output}
        
        REQUIRED: {req}
        FORBIDDEN: {forb}
        
        Return JSON ONLY:
        {{
            "present": ["elem1"],
            "missing": ["elem2"],
            "forbidden_found": [],
            "reasoning": "text"
        }}
        """

        try:
            # Try with just the model name first
            model_id = Config.DEFAULT_GEMINI_MODEL # e.g. "gemini-1.5-flash"
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            content = response.text.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
        except Exception as e:
            logger.error(f"GRADING ERROR for {task_id}: {str(e)}")
            result = {
                "present": [],
                "missing": req,
                "forbidden_found": [],
                "reasoning": f"LLM Grading Failure: {str(e)}",
            }

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
            grading_reasoning=result.get("reasoning", ""),
        )
