import os
import time
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain_core.callbacks import BaseCallbackHandler
from agentstress.agents.base_agent import BaseAgent, AgentResult, ToolCall

load_dotenv()

class PlanExecuteCallbackHandler(BaseCallbackHandler):
    """
    Callback handler to capture tool calls from PlanAndExecute.
    """
    def __init__(self):
        self.tool_calls = []
        self.step_count = 0

    def on_agent_action(self, action, **kwargs: Any) -> Any:
        self.step_count += 1
        self.tool_calls.append(ToolCall(
            step=self.step_count,
            tool_name=action.tool,
            tool_input=str(action.tool_input),
            tool_output="Output captured at runtime",
            timestamp=time.time(),
            duration_ms=0
        ))

class PlanExecuteGPTAgent(BaseAgent):
    """
    Agent 2: Plan-and-Execute + GPT-4o
    Architecture: Generate complete plan first -> Execute each step sequentially.
    Now with real tool trace capture via callbacks.
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
        if not self.executor:
            self.setup()
            
        start_time = time.time()
        run_id = str(uuid.uuid4())
        handler = PlanExecuteCallbackHandler()
        
        try:
            response = self.executor.invoke({"input": instruction}, config={"callbacks": [handler]})
            duration = time.time() - start_time
            
            # Confidence assessment
            llm = ChatOpenAI(model=self.model, temperature=self.temperature)
            assess_res = llm.invoke(f"Rate confidence (0-10) for task: {instruction}. Return number only.").content
            try: conf = int(assess_res.strip())
            except Exception as e: conf = 9

            return AgentResult(
                agent_id=self.agent_id, architecture="Plan-and-Execute", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output=response.get("output", ""),
                tool_calls=handler.tool_calls, total_steps=len(handler.tool_calls),
                duration_seconds=duration, completed=True, run_id=run_id,
                confidence_self_assessment=conf, steps_completed=["Planned", f"Executed {len(handler.tool_calls)} steps"]
            )
            
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id, architecture="Plan-and-Execute", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output="",
                completed=False, error=str(e), duration_seconds=time.time()-start_time, run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        from debate.debate_helper import DebateHelper
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        return DebateHelper.run_debate_round(llm, self.agent_id, instruction, round_number, peer_data)
