import os
import time
import uuid
import requests
from typing import List, Dict, Any, Optional
from agentstress.agents.base_agent import BaseAgent, AgentResult, ToolCall
from agentstress.config import Config
from agentstress import logger

class OllamaAgent(BaseAgent):
    """
    Local AI Agent powered by Ollama.
    The core of the $0 cost reliability roadmap.
    """
    
    def __init__(self, agent_id: str = "local_ollama_agent", model: str = None, temperature: float = 0.1):
        # Use default model from config if not specified
        model = model or Config.DEFAULT_LOCAL_MODEL
        super().__init__(agent_id, model, temperature)
        self.base_url = f"{Config.OLLAMA_BASE_URL}/api/generate"

    def setup(self) -> None:
        """Verify Ollama is reachable."""
        try:
            res = requests.get(Config.OLLAMA_BASE_URL, timeout=2)
            if res.status_code == 200:
                logger.info(f"Ollama reachable at {Config.OLLAMA_BASE_URL}")
        except Exception:
            logger.warning(f"Ollama NOT reachable at {Config.OLLAMA_BASE_URL}. Experiments will fail.")

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Executes task locally via Ollama."""
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        payload = {
            "model": self.model,
            "prompt": instruction,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            output = data.get("response", "")
            
            duration = time.time() - start_time
            
            # Simple Ollama agents don't use tools in this basic wrapper, 
            # but we record the 'thought' step.
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Local-Ollama",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output=output,
                tool_calls=[],
                total_steps=1,
                duration_seconds=duration,
                completed=True,
                run_id=run_id,
                confidence_self_assessment=8,
                steps_completed=["Local Generation"]
            )
            
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                architecture="Local-Ollama",
                model=self.model,
                instruction=instruction,
                instruction_type=instruction_type,
                output="",
                completed=False,
                error=str(e),
                duration_seconds=time.time()-start_time,
                run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Debate round running locally."""
        prompt = f"System: You are in a multi-agent debate. Task: {instruction}\nRound: {round_number}\nPeer Data: {peer_data}\nProvide your refined answer."
        
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            res = requests.post(self.base_url, json=payload)
            return {"agent_id": self.agent_id, "response": res.json().get("response", "")}
        except:
            return {"agent_id": self.agent_id, "response": "Error in local generation."}
