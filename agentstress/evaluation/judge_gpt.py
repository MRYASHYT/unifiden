import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tenacity import retry, wait_exponential, stop_after_attempt
from agentstress.evaluation.rubric_engine import RubricScore, RubricEngine
from agentstress.evaluation.base_judge import BaseJudge, FailureClassification, DebateJudgment


class GPTJudge(BaseJudge):
    """
    Primary judge using GPT-4o to classify failures and score rubrics.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.llm = None
        self.rubric_engine = RubricEngine()
        self.taxonomy = {
            "NO_FAILURE": "Task completed accurately and completely.",
            "INSTRUCTION_DRIFT": "Final answer addresses a related but different goal.",
            "PREMATURE_TERMINATION": "Stopped before completing all required elements.",
            "TOOL_CALL_HALLUCINATION": "Stated facts or data that are fabricated.",
            "OVERCONFIDENCE_COLLAPSE": "Abandoned a correct answer due to peer pressure.",
            "STUBBORN_FAILURE": "Did not update wrong beliefs despite peer correction.",
            "CONTAMINATION": "Adopted a peer's hallucination as fact.",
            "PARTIAL_FAILURE": "Acknowledged incompleteness but did not attempt recovery.",
        }

    def _setup_llm(self):
        if self.llm is None:
            self.llm = ChatOpenAI(model=self.model, temperature=0)

    def score_rubric(
        self, task_id: str, instruction: str, agent_output: str, rubric: dict
    ) -> RubricScore:
        return self.rubric_engine.score_output(task_id, "GPT_JUDGE", agent_output, rubric)

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]],
    ) -> FailureClassification:
        self._setup_llm()
        prompt = ChatPromptTemplate.from_template("""
        You are the AgentStress Judge. Your task is to classify an agent's failure based on a strict taxonomy.
        
        TAXONOMY:
        {taxonomy}
        
        ORIGINAL INSTRUCTION ({instruction_type}):
        {instruction}
        
        AGENT OUTPUT:
        {agent_output}
        
        RUBRIC SCORE:
        {rubric_score_percent}% completeness.
        
        Analyze the behavior and return JSON:
        - failure_mode: (Name from taxonomy)
        - confidence: (0-10)
        - evidence: (Quote/Step)
        - drift_score: (0-10)
        - completeness_score: (0-10)
        - hallucination_detected: (true/false)
        - hallucination_content: (Optional)
        - reasoning: (Explanation)
        """)

        chain = prompt | self.llm

        @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
        def invoke_chain():
            return chain.invoke(
                {
                    "taxonomy": json.dumps(self.taxonomy, indent=2),
                    "instruction": instruction,
                    "instruction_type": instruction_type,
                    "agent_output": agent_output,
                    "rubric_score_percent": rubric_score.percentage,
                }
            )

        response = invoke_chain()

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            data = json.loads(content)
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode=data.get("failure_mode", "UNKNOWN"),
                confidence=data.get("confidence", 0),
                evidence=data.get("evidence", ""),
                drift_score=data.get("drift_score", 0),
                completeness_score=data.get("completeness_score", 0),
                hallucination_detected=data.get("hallucination_detected", False),
                hallucination_content=data.get("hallucination_content"),
                reasoning=data.get("reasoning", ""),
            )
        except Exception as e:
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode="ERROR_PARSING",
                confidence=0,
                evidence="N/A",
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning=str(e),
            )

    def judge_debate(
        self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict
    ) -> DebateJudgment:
        return DebateJudgment(
            task=task,
            instruction_type="N/A",
            ground_truth="Scaffolded",
            agent_scores={},
            hallucination_propagation={},
            reliability_ranking=[],
            production_recommendation="N/A",
            framework_insights=[],
            overall_reliability_score=0,
            experiment_metadata={},
        )
