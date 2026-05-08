import os
import time
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchainhub import Client
from langchain_core.prompts import ChatPromptTemplate
import json
from agentstress.agents.base_agent import BaseAgent, AgentResult, ToolCall

load_dotenv()

class ReActGPTAgent(BaseAgent):
    """
    Agent 1: ReAct + GPT-4o
    Baseline production architecture for the AgentStress framework.
    """
    
    def __init__(self, agent_id: str = "agent_1_react_gpt4o", model: str = "gpt-4o", temperature: float = 0.1):
        super().__init__(agent_id, model, temperature)
        self.executor = None
        self.tools = [DuckDuckGoSearchRun()]

    def setup(self) -> None:
        """Initialize the LangChain ReAct agent."""
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        client = Client()
        prompt = client.pull("hwchase17/react")
        agent = create_react_agent(llm, self.tools, prompt)
        self.executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=15,
            return_intermediate_steps=True
        )

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Executes the task and captures detailed execution traces."""
        if not self.executor:
            self.setup()
            
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        try:
            response = self.executor.invoke({"input": instruction})
            duration = time.time() - start_time
            
            # Parse intermediate steps into ToolCall objects
            tool_calls = []
            for i, (action, observation) in enumerate(response.get("intermediate_steps", [])):
                tool_calls.append(ToolCall(
                    step=i + 1,
                    tool_name=action.tool,
                    tool_input=str(action.tool_input),
                    tool_output=str(observation),
                    timestamp=time.time(),
                    duration_ms=0
                ))
            
            # Ask the LLM for self-assessment
            assessment_prompt = f"Based on your performance on this task, rate your confidence from 0-10 and list the steps you completed. Return JSON: {{\"confidence\": int, \"steps\": [list]}}"
            assessment = self.executor.invoke({"input": assessment_prompt})
            try:
                import re
                conf_match = re.search(r'"confidence":\s*(\d+)', assessment["output"])
                confidence = int(conf_match.group(1)) if conf_match else 7
            except Exception as e: confidence = 7

            return AgentResult(
                agent_id=self.agent_id,
                architecture="ReAct",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=response.get("output", ""),
                tool_calls=tool_calls,
                total_steps=len(tool_calls),
                duration_seconds=duration,
                completed=True,
                run_id=run_id,
                confidence_self_assessment=confidence,
                steps_completed=[f"Step {i+1}: {tc.tool_name}" for i, tc in enumerate(tool_calls)]
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return AgentResult(
                agent_id=self.agent_id,
                architecture="ReAct",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output="",
                completed=False,
                error=str(e),
                duration_seconds=duration,
                run_id=run_id
            )

    def run_with_peer_context(
        self, 
        instruction: str,
        round_number: int,
        peer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        from agentstress.debate.debate_helper import DebateHelper
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        return DebateHelper.run_debate_round(llm, self.agent_id, instruction, round_number, peer_data)

if __name__ == "__main__":
    agent = ReActGPTAgent()
    print(f"Running Agent: {agent.agent_id}")
