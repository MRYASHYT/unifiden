import os
import time
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from agents.base_agent import BaseAgent, AgentResult, ToolCall

load_dotenv()

class PlanExecuteGPTAgent(BaseAgent):
    """
    Agent 2: Plan-and-Execute + GPT-4o
    Patterns: Generate complete plan first -> Execute each step sequentially.
    """
    
    def __init__(self, agent_id: str = "agent_2_plan_execute", model: str = "gpt-4o", temperature: float = 0.1):
        super().__init__(agent_id, model, temperature)
        self.executor = None
        self.tools = [DuckDuckGoSearchRun()]

    def setup(self) -> None:
        """Initialize the Plan-and-Execute agent."""
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        planner = load_chat_planner(llm)
        executor = load_agent_executor(llm, self.tools, verbose=True)
        self.executor = PlanAndExecute(planner=planner, executor=executor, verbose=True)

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Executes the task and captures execution traces."""
        if not self.executor:
            self.setup()
            
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        try:
            response = self.executor.invoke({"input": instruction})
            duration = time.time() - start_time
            
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Plan-and-Execute",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=response.get("output", ""),
                tool_calls=[],
                total_steps=0,
                duration_seconds=duration,
                completed=True,
                run_id=run_id,
                confidence_self_assessment=9,
                steps_completed=["Planned and executed steps"]
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Plan-and-Execute",
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
    agent = PlanExecuteGPTAgent()
    print(f"Running Agent: {agent.agent_id}")
