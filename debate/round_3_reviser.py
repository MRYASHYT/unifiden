from typing import List, Dict, Any
import dataclasses
from agents.base_agent import BaseAgent

class Round3Reviser:
    """
    Each agent receives peer reviews and its own Round 1 answer to produce a final revised answer.
    """
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, instruction: str, round1_results: Dict[str, Any], round2_results: Dict[str, Any]) -> Dict[str, Any]:
        revised_answers = {}
        for agent in self.agents:
            print(f"  Agent {agent.agent_id} revising answer...")
            
            # Context includes: own Round 1, peer reviews of self, self reviews of peers
            # Simplified for MVP: focus on peer reviews of self
            peer_context = {
                "round1_own": dataclasses.asdict(round1_results[agent.agent_id]),
                "peer_reviews": round2_results # In full version, filter specifically for this agent
            }
            
            revised = agent.run_with_peer_context(instruction, 3, peer_context)
            revised_answers[agent.agent_id] = revised
            
        return revised_answers
