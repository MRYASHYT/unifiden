import os
import time
import uuid
import requests
import json
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
        model = model or Config.DEFAULT_LOCAL_MODEL
        super().__init__(agent_id, model, temperature)
        # Use generate endpoint
        self.base_url = f"{Config.OLLAMA_BASE_URL}/api/generate"

    def setup(self) -> None:
        """Verify Ollama is reachable and model is available."""
        try:
            res = requests.get(Config.OLLAMA_BASE_URL, timeout=5)
            if res.status_code == 200:
                logger.info(f"Ollama server is active at {Config.OLLAMA_BASE_URL}")
        except Exception:
            logger.warning(f"Ollama server NOT found at {Config.OLLAMA_BASE_URL}.")

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Executes task locally via Ollama with robust error handling."""
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        # Simplified payload to maximize compatibility
        payload = {
            "model": self.model,
            "prompt": instruction,
            "stream": False
        }
        
        try:
            # Increased timeout for local heavy-lifting
            response = requests.post(self.base_url, json=payload, timeout=300)
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", error_detail)
                except: pass
                raise Exception(f"Ollama Error ({response.status_code}): {error_detail}")
                
            data = response.json()
            output = data.get("response", "")
            
            duration = time.time() - start_time
            
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
            logger.error(f"Ollama Execution Failed: {str(e)}")
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
        prompt = f"System: Multi-agent debate.\nTask: {instruction}\nRound: {round_number}\nPeers: {json.dumps(peer_data)}\nRefined Answer:"
        
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            res = requests.post(self.base_url, json=payload, timeout=300)
            return {"agent_id": self.agent_id, "response": res.json().get("response", "")}
        except Exception as e:
            return {"agent_id": self.agent_id, "response": f"Error: {str(e)}"}
