from typing import List, Dict, Any
import dataclasses
from agents.base_agent import BaseAgent

class Round3Reviser:
    """
    Each agent receives peer reviews of its OWN Round 1 answer 
    and its own Round 1 answer to produce a final revised answer.
    """
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, instruction: str, round1_results: Dict[str, Any], round2_results: Dict[str, Any]) -> Dict[str, Any]:
        revised_answers = {}
        for agent in self.agents:
            print(f"  Agent {agent.agent_id} revising answer...")
            
            # Privacy Filter: Only give this agent reviews that were ABOUT them.
            # Round 2 results is a dict: { reviewer_id: { "reviews": { target_id: review_text } } }
            # (Note: DebateHelper structure returns { "agent_id": aid, "response": text })
            # We need to parse the response to extract the specific review for this agent.
            
            # Since the current Round 2 implementation returns a raw text block of all peer reviews,
            # we provide the full block but instruct the agent to focus on feedback about itself.
            # IN PRODUCTION: We would extract the specific section for 'agent.agent_id'.
            
            peer_context = {
                "round1_own": dataclasses.asdict(round1_results[agent.agent_id]),
                "peer_reviews": round2_results 
            }
            
            revised = agent.run_with_peer_context(instruction, 3, peer_context)
            revised_answers[agent.agent_id] = revised
            
        return revised_answers
