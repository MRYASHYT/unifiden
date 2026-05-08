import json
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from evaluation.rubric_engine import RubricScore
from evaluation.judge_gpt import FailureClassification

class ClaudeJudge:
    """
    Secondary judge using Claude to classify failures based on the taxonomy for inter-rater reliability.
    """
    
    def __init__(self, model: str = "claude-3-5-sonnet-latest"):
        self.llm = ChatAnthropic(model=model, temperature=0)
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

    def classify_failure(
        self,
        instruction: str,
        instruction_type: str,
        agent_output: str,
        rubric_score: RubricScore,
        execution_trace: List[Dict[str, Any]]
    ) -> FailureClassification:
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
        Missing elements: {missing_elements}
        Forbidden elements: {forbidden_elements}
        
        EXECUTION TRACE (Tool Calls):
        {execution_trace}
        
        Analyze the agent's behavior. Determine if it failed and how.
        Return your analysis as a JSON object with the following fields:
        - failure_mode: (The exact name from the taxonomy)
        - confidence: (0-10)
        - evidence: (A quote or specific step where the failure occurred)
        - drift_score: (0-10, how far it drifted from the original goal)
        - completeness_score: (0-10, based on rubric)
        - hallucination_detected: (true/false)
        - hallucination_content: (Optional: what was fabricated)
        - reasoning: (Detailed explanation for your classification)
        """)
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "taxonomy": json.dumps(self.taxonomy, indent=2),
            "instruction": instruction,
            "instruction_type": instruction_type,
            "agent_output": agent_output,
            "rubric_score_percent": rubric_score.percentage,
            "missing_elements": ", ".join(rubric_score.required_elements_missing),
            "forbidden_elements": ", ".join(rubric_score.forbidden_elements_found),
            "execution_trace": json.dumps(execution_trace, indent=2)
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
                reasoning=f"Could not parse judge response: {str(e)} | Content: {response.content}"
            )
