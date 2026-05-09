import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os

from agentstress.config import Config


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
        self.model = None

    def _setup_gemini(self):
        if self.model is None:
            from google import genai

            client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            self.model = Config.DEFAULT_GEMINI_MODEL
            self.client = client

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
        You are an elite technical auditor. Evaluate the agent's response against the provided rubric with extreme precision.
        
        TASK INSTRUCTION:
        {task_id}
        
        AGENT RESPONSE:
        \"\"\"{output}\"\"\"
        
        REQUIRED SEMANTIC ELEMENTS:
        {req}
        
        FORBIDDEN ELEMENTS (STRICT NEGATIVE CONSTRAINT):
        {forb}
        
        GRADING CRITERIA:
        1. REQUIRED: An element is 'present' only if its core semantic meaning is fully captured.
        2. FORBIDDEN: Any mention or usage of forbidden elements results in a 'forbidden_found' entry.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "present": ["semantic_element_1", ...],
            "missing": ["semantic_element_2", ...],
            "forbidden_found": ["violation_1", ...],
            "reasoning": "Detailed technical justification for the grade."
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=Config.DEFAULT_GEMINI_MODEL, contents=prompt
            )
            content = response.text.strip()
            # Handle markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:].strip()

            result = json.loads(content)
        except Exception as e:
            # High-reliability fallback with error logging
            print(f"GRADING ERROR for {task_id}: {str(e)}")
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
