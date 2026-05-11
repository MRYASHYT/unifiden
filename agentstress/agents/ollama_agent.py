import os
import time
import uuid
import requests
import json
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from tenacity import retry, wait_exponential, stop_after_attempt

from agentstress.agents.base_agent import BaseAgent, AgentResult, ToolCall
from agentstress.agents.react_prompt import build_react_prompt
from agentstress.config import Config
from agentstress import logger

class OllamaAgent(BaseAgent):
    """
    Local AI Agent powered by Ollama + ReAct.
    The core of the $0 cost reliability roadmap.
    """
    
    def __init__(self, agent_id: str = "local_ollama_agent", model: str = None, temperature: float = 0.1):
        model = model or Config.DEFAULT_LOCAL_MODEL
        super().__init__(agent_id, model, temperature)
        self.base_url = f"{Config.OLLAMA_BASE_URL}/api/generate"
        self.executor = None
        self.tools = [DuckDuckGoSearchRun()]

    def setup(self) -> None:
        """Initialize the LangChain ReAct agent with local Ollama."""
        try:
            # Verify Ollama is reachable
            res = requests.get(Config.OLLAMA_BASE_URL, timeout=5)
            if res.status_code == 200:
                logger.info(f"Ollama server is active at {Config.OLLAMA_BASE_URL}")
            
            # Setup LangChain ReAct
            llm = ChatOllama(
                base_url=Config.OLLAMA_BASE_URL,
                model=self.model,
                temperature=self.temperature
            )
            prompt = build_react_prompt()
            agent = create_react_agent(llm, self.tools, prompt)
            self.executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10,
                return_intermediate_steps=True,
            )
        except Exception as e:
            logger.error(f"Ollama Agent Setup Failed: {str(e)}")

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Executes task locally via Ollama with ReAct loop."""
        if not self.executor:
            self.setup()
            
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        # If setup failed and no executor, fallback to direct completion
        if not self.executor:
            return self._run_direct_fallback(instruction, instruction_type, start_time, run_id)

        try:
            @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(2))
            def invoke_agent():
                return self.executor.invoke({"input": instruction})

            response = invoke_agent()
            duration = time.time() - start_time

            # Parse intermediate steps into ToolCall objects
            tool_calls = []
            for i, (action, observation) in enumerate(response.get("intermediate_steps", [])):
                tool_calls.append(
                    ToolCall(
                        step=i + 1,
                        tool_name=action.tool,
                        tool_input=str(action.tool_input),
                        tool_output=str(observation),
                        timestamp=time.time(),
                        duration_ms=0,
                    )
                )

            return AgentResult(
                agent_id=self.agent_id,
                architecture="Local-Ollama-ReAct",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=response.get("output", ""),
                tool_calls=tool_calls,
                total_steps=len(tool_calls),
                duration_seconds=duration,
                completed=True,
                run_id=run_id,
                confidence_self_assessment=7,
                steps_completed=[f"Step {i+1}: {tc.tool_name}" for i, tc in enumerate(tool_calls)],
            )
            
        except Exception as e:
            logger.warning(f"Ollama ReAct failed, falling back to direct: {str(e)}")
            return self._run_direct_fallback(instruction, instruction_type, start_time, run_id)

    def _run_direct_fallback(self, instruction: str, instruction_type: str, start_time: float, run_id: str) -> AgentResult:
        """Fallback to a single direct completion call."""
        payload = {
            "model": self.model,
            "prompt": instruction,
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=300)
            data = response.json()
            output = data.get("response", "")
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Local-Ollama-Direct",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=output,
                completed=True,
                duration_seconds=time.time() - start_time,
                run_id=run_id
            )
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Local-Ollama-Fallback",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output="",
                completed=False,
                error=str(e),
                duration_seconds=time.time() - start_time,
                run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Debate round running locally."""
        prompt = f"System: Multi-agent debate.\nTask: {instruction}\nRound: {round_number}\nPeers: {json.dumps(peer_data)}\nRefined Answer:"
        
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            res = requests.post(self.base_url, json=payload, timeout=300)
            return {"agent_id": self.agent_id, "response": res.json().get("response", "")}
        except Exception as e:
            return {"agent_id": self.agent_id, "response": f"Error: {str(e)}"}

