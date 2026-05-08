import dataclasses
from typing import List, Dict, Any
from agentstress.agents.base_agent import BaseAgent

class Round2Reviewer:
    """
    Each agent reviews the Round 1 answers of all other agents.
    """
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, instruction: str, round1_results: Dict[str, Any]) -> Dict[str, Any]:
        all_reviews = {}
        for reviewer in self.agents:
            print(f"  Agent {reviewer.agent_id} reviewing peers...")
            # Filter out the reviewer's own result
            peers_data = {
                aid: dataclasses.asdict(res) 
                for aid, res in round1_results.items() 
                if aid != reviewer.agent_id
            }
            
            # Logic for peer review would be an LLM call within run_with_peer_context
            review = reviewer.run_with_peer_context(instruction, 2, peers_data)
            all_reviews[reviewer.agent_id] = review
            
        return all_reviews
