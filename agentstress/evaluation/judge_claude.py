import json
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from agentstress.evaluation.rubric_engine import RubricScore, RubricEngine
from agentstress.evaluation.base_judge import BaseJudge, FailureClassification, DebateJudgment

class ClaudeJudge(BaseJudge):
    """
    Secondary judge using Claude for inter-rater reliability.
    """
    
    def __init__(self, model: str = "claude-3-5-sonnet-latest"):
        self.llm = ChatAnthropic(model=model, temperature=0)
        self.rubric_engine = RubricEngine()
        self.taxonomy = {
            "NO_FAILURE": "Task completed accurately and completely.",
            "INSTRUCTION_DRIFT": "Final answer addresses a related but different goal.",
            "PREMATURE_TERMINATION": "Stopped before completing all required elements.",
            "TOOL_CALL_HALLUCINATION": "Stated facts or data that are fabricated.",
            "OVERCONFIDENCE_COLLAPSE": "Abandoned a correct answer due to peer pressure.",
            "STUBBORN_FAILURE": "Did not update wrong beliefs despite peer correction.",
            "CONTAMINATION": "Adopted a peer's hallucination as fact.",
            "PARTIAL_FAILURE": "Acknowledged incompleteness but did not attempt recovery."
        }

    def score_rubric(self, task_id: str, instruction: str, agent_output: str, rubric: dict) -> RubricScore:
        return self.rubric_engine.score_output(task_id, "CLAUDE_JUDGE", agent_output, rubric)

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]]
    ) -> FailureClassification:
        prompt = ChatPromptTemplate.from_template("""
        You are the AgentStress Judge (Claude Edition). Your task is to classify an agent's failure based on a strict taxonomy.
        
        TAXONOMY:
        {taxonomy}
        
        ORIGINAL INSTRUCTION ({instruction_type}):
        {instruction}
        
        AGENT OUTPUT:
        {agent_output}
        
        RUBRIC SCORE:
        {rubric_score_percent}% completeness.
        
        Analyze the agent's behavior and return your analysis as a JSON object:
        - failure_mode: (The exact name from the taxonomy)
        - confidence: (0-10)
        - evidence: (A quote or specific step where the failure occurred)
        - drift_score: (0-10)
        - completeness_score: (0-10)
        - hallucination_detected: (true/false)
        - hallucination_content: (Optional)
        - reasoning: (Detailed explanation)
        """)
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "taxonomy": json.dumps(self.taxonomy, indent=2),
            "instruction": instruction,
            "instruction_type": instruction_type,
            "agent_output": agent_output,
            "rubric_score_percent": rubric_score.percentage
        })
        
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
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            return FailureClassification(
                agent_id=rubric_score.agent_id,
                failure_mode="ERROR_PARSING_JUDGMENT",
                confidence=0,
                evidence="N/A",
                drift_score=0,
                completeness_score=0,
                hallucination_detected=False,
                hallucination_content=None,
                reasoning=f"Claude Judge Parse Error: {str(e)}"
            )

    def judge_debate(self, task: str, round_1_answers: dict, round_2_reviews: dict, round_3_answers: dict) -> DebateJudgment:
        return DebateJudgment(
            task=task, instruction_type="N/A", ground_truth="Final Ground Truth calculated by Round4Judge",
            agent_scores={}, hallucination_propagation={}, reliability_ranking=[],
            production_recommendation="N/A", framework_insights=[],
            overall_reliability_score=0, experiment_metadata={}
        )
