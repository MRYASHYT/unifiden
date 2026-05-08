import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

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

class RubricEngine:
    """
    Implements objective rubric-based scoring to prevent judge hallucination.
    Follows the structure defined in unifiden_complete_spec.md.
    """
    
    def __init__(self, rubrics_path: str = "tasks/rubrics.json"):
        self.rubrics_path = rubrics_path
        self.rubrics = self._load_rubrics()

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
        """
        Scores an agent's output against a specific rubric.
        If rubric_data is provided, it uses that; otherwise, it looks up by task_id.
        """
        rubric = rubric_data or self.rubrics.get(task_id)
        
        if not rubric:
            raise ValueError(f"Rubric for task {task_id} not found.")

        required_elements = rubric.get("required_elements", [])
        forbidden_elements = rubric.get("forbidden_elements", [])
        
        present = []
        missing = []
        forbidden_found = []
        
        # Check required elements (simple keyword/phrase check for MVP)
        # In a real scenario, this could be enhanced with LLM-based checklist checking
        for element in required_elements:
            if element.lower() in output.lower():
                present.append(element)
            else:
                missing.append(element)
                
        # Check forbidden elements
        for element in forbidden_elements:
            if element.lower() in output.lower():
                forbidden_found.append(element)
                
        # Calculate scores
        # scoring: { required_present: +1, forbidden_present: -2 }
        raw_score = len(present) - (len(forbidden_found) * 2)
        max_score = len(required_elements)
        
        # Ensure raw_score doesn't go below 0 for percentage
        percentage = (max(0, raw_score) / max_score * 100) if max_score > 0 else 0.0
        
        return RubricScore(
            task_id=task_id,
            agent_id=agent_id,
            required_elements_present=present,
            required_elements_missing=missing,
            forbidden_elements_found=forbidden_found,
            raw_score=raw_score,
            max_score=max_score,
            percentage=percentage
        )

if __name__ == "__main__":
    # Test Rubric Engine
    engine = RubricEngine()
    test_rubric = {
        "required_elements": ["Paper 1", "Paper 2", "Paper 3"],
        "forbidden_elements": ["Fabricated Result"]
    }
    test_output = "I found Paper 1 and Paper 2. No Paper 3. Here is a Fabricated Result."
    
    score = engine.score_output("test_task", "agent_1", test_output, test_rubric)
    print(f"Score: {score.percentage}%")
    print(f"Missing: {score.required_elements_missing}")
    print(f"Forbidden Found: {score.forbidden_elements_found}")
