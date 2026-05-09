from typing import List, Dict, Any
import dataclasses
from agentstress.agents.base_agent import BaseAgent, AgentResult


class Round1Runner:
    """
    Executes all agents independently on the same instruction.
    """

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, instruction: str, instruction_type: str) -> Dict[str, AgentResult]:
        results = {}
        for agent in self.agents:
            print(f"  Agent {agent.agent_id} executing...")
            result = agent.run(instruction, instruction_type)
            results[agent.agent_id] = result
        return results
