import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import requests
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
    Supports both Gemini (Cloud) and Ollama (Local) for grading.
    """

    def __init__(self, rubrics_path: str = None):
        self.rubrics_path = rubrics_path or os.path.join(Config.TASKS_DIR, "rubrics.json")
        self.rubrics = self._load_rubrics()
        self.model_type = None # 'gemini' or 'ollama'
        self.client = None

    def _setup_judge(self):
        if self.model_type is None:
            # Prefer Ollama if in local mode to avoid rate limits
            if os.getenv("AGENTSTRESS_LOCAL") == "True" or not Config.GOOGLE_API_KEY:
                self.model_type = "ollama"
                logger.info("RubricEngine: Using local Ollama for grading.")
                return
            
            try:
                from google import genai
                self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
                self.model_type = "gemini"
                logger.info("RubricEngine: Using Gemini Cloud for grading.")
            except Exception as e:
                logger.warning(f"Gemini init failed, falling back to Ollama: {str(e)}")
                self.model_type = "ollama"

    def _load_rubrics(self) -> Dict[str, Any]:
        try:
            with open(self.rubrics_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def score_output(
        self, task_id: str, agent_id: str, output: str, rubric_data: Optional[Dict[str, Any]] = None
    ) -> RubricScore:
        self._setup_judge()
        rubric = rubric_data or self.rubrics.get(task_id)
        if not rubric:
            raise ValueError(f"Rubric for task {task_id} not found.")

        req = rubric.get("required_elements", [])
        forb = rubric.get("forbidden_elements", [])

        prompt = f"""
        [SYSTEM: INDUSTRIAL GRADER]
        Return JSON ONLY:
        {{
            "present": ["elem1"],
            "missing": ["elem2"],
            "forbidden_found": [],
            "reasoning": "text"
        }}
        TASK: {task_id}
        RESPONSE: {output}
        REQUIRED: {req}
        """

        content = "{}"
        try:
            if self.model_type == "ollama":
                payload = {"model": Config.DEFAULT_LOCAL_MODEL, "prompt": prompt, "stream": False, "format": "json"}
                res = requests.post(f"{Config.OLLAMA_BASE_URL}/api/generate", json=payload, timeout=300)
                content = res.json().get("response", "{}")
            else:
                response = self.client.models.generate_content(
                    model=Config.DEFAULT_GEMINI_MODEL,
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
                "reasoning": f"Grading Failure: {str(e)}",
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
