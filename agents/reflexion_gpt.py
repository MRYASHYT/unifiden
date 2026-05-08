import os
import time
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent, AgentResult, ToolCall

load_dotenv()

class ReflexionGPTAgent(BaseAgent):
    """
    Agent 3: Reflexion + GPT-4o
    Pattern: Execute -> Self-critique -> Revise -> Execute again.
    """
    
    def __init__(self, agent_id: str = "agent_3_reflexion", model: str = "gpt-4o", temperature: float = 0.1):
        super().__init__(agent_id, model, temperature)
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self.tools = [DuckDuckGoSearchRun()]

    def setup(self) -> None:
        pass

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        try:
            # Step 1: Initial Generation
            initial_prompt = ChatPromptTemplate.from_template("Task: {input}\nGenerate a detailed answer.")
            initial_response = self.llm.invoke(initial_prompt.format(input=instruction))
            initial_answer = initial_response.content
            
            # Step 2: Self-Critique
            critique_prompt = ChatPromptTemplate.from_template(
                "Task: {input}\nInitial Answer: {answer}\nCritique this answer for accuracy and completeness. List specifically what is wrong or missing."
            )
            critique_response = self.llm.invoke(critique_prompt.format(input=instruction, answer=initial_answer))
            critique = critique_response.content
            
            # Step 3: Revision
            revision_prompt = ChatPromptTemplate.from_template(
                "Task: {input}\nInitial Answer: {answer}\nCritique: {critique}\nBased on the critique, provide a final, improved, and accurate answer."
            )
            final_response = self.llm.invoke(revision_prompt.format(input=instruction, answer=initial_answer, critique=critique))
            final_answer = final_response.content
            
            duration = time.time() - start_time
            
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Reflexion",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=final_answer,
                tool_calls=[], # This simplified version doesn't use tools in every step, can be expanded
                total_steps=3,
                duration_seconds=duration,
                completed=True,
                run_id=run_id,
                confidence_self_assessment=9,
                steps_completed=["Initial Gen", "Self-Critique", "Revision"]
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Reflexion",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output="",
                completed=False,
                error=str(e),
                duration_seconds=duration,
                run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        from debate.debate_helper import DebateHelper
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        return DebateHelper.run_debate_round(llm, self.agent_id, instruction, round_number, peer_data)

if __name__ == "__main__":
    agent = ReflexionGPTAgent()
    print(f"Running Agent: {agent.agent_id}")
