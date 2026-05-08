import os
import time
import uuid
import json
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
    Architecture: Execute -> Self-critique -> Revise -> Final Answer.
    Uses real tools during the execution phase.
    """
    
    def __init__(self, agent_id: str = "agent_3_reflexion", model: str = "gpt-4o", temperature: float = 0.1):
        super().__init__(agent_id, model, temperature)
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self.search = DuckDuckGoSearchRun()

    def setup(self) -> None:
        pass

    def _execute_with_tools(self, instruction: str) -> Dict[str, Any]:
        """Performs initial task execution with tool use."""
        prompt = ChatPromptTemplate.from_template("""
        Task: {input}
        You have access to a search tool. Perform a search to gather information, then provide a detailed draft answer.
        First, output your search query in the format: SEARCH: [query]
        Then, based on the results, write your draft.
        """)
        
        # Step 1: Generate Search Query
        initial_response = self.llm.invoke(prompt.format(input=instruction))
        content = initial_response.content
        
        tool_calls = []
        search_result = ""
        if "SEARCH:" in content:
            query = content.split("SEARCH:")[1].split("\n")[0].strip()
            search_result = self.search.run(query)
            tool_calls.append(ToolCall(
                step=1, tool_name="DuckDuckGo", tool_input=query, tool_output=search_result, 
                timestamp=time.time(), duration_ms=0
            ))
            
            # Step 2: Finalize Draft with search data
            draft_prompt = ChatPromptTemplate.from_template("Task: {input}\nSearch Results: {results}\nWrite a complete draft answer.")
            draft_res = self.llm.invoke(draft_prompt.format(input=instruction, results=search_result))
            content = draft_res.content

        return {"output": content, "tool_calls": tool_calls}

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        try:
            # 1. Execution
            execution = self._execute_with_tools(instruction)
            draft = execution["output"]
            
            # 2. Self-Critique
            critique_prompt = ChatPromptTemplate.from_template(
                "Task: {input}\nInitial Draft: {draft}\nCritique this for accuracy, completeness, and potential hallucinations. Be harsh."
            )
            critique = self.llm.invoke(critique_prompt.format(input=instruction, draft=draft)).content
            
            # 3. Revision
            revision_prompt = ChatPromptTemplate.from_template(
                "Task: {input}\nDraft: {draft}\nCritique: {critique}\nProvide the final, corrected, and most accurate version."
            )
            final_answer = self.llm.invoke(revision_prompt.format(input=instruction, draft=draft, critique=critique)).content
            
            duration = time.time() - start_time
            
            # Self-assessment
            assess_res = self.llm.invoke(f"Rate your confidence (0-10) for this task: {instruction}. Return only the number.").content
            try: confidence = int(assess_res.strip())
            except Exception as e: confidence = 8

            return AgentResult(
                agent_id=self.agent_id, architecture="Reflexion", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output=final_answer,
                tool_calls=execution["tool_calls"], total_steps=3 + len(execution["tool_calls"]),
                duration_seconds=duration, completed=True, run_id=run_id,
                confidence_self_assessment=confidence, steps_completed=["Execute", "Critique", "Revise"]
            )
            
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id, architecture="Reflexion", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output="",
                completed=False, error=str(e), duration_seconds=time.time()-start_time, run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        from debate.debate_helper import DebateHelper
        return DebateHelper.run_debate_round(self.llm, self.agent_id, instruction, round_number, peer_data)
