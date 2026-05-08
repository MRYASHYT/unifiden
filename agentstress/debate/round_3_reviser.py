from typing import List, Dict, Any
import dataclasses
from agentstress.agents.base_agent import BaseAgent

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
            # round2_results structure: { reviewer_id: { "agent_id": target_id, "response": review_text } }
            # Actually, DebateHelper.run_debate_round returns { "agent_id": reviewer_id, "round": 2, "response": combined_reviews }
            
            # For each reviewer's response, we extract the part intended for 'agent.agent_id'
            relevant_reviews = {}
            for reviewer_id, review_bundle in round2_results.items():
                # For MVP, we pass the full bundle but instruct the LLM specifically to look for reviews of self.
                # In full implementation, we would regex parse the bundle or use structured output.
                relevant_reviews[reviewer_id] = review_bundle.get("response", "")
            
            peer_context = {
                "round1_own": dataclasses.asdict(round1_results[agent.agent_id]),
                "peer_reviews_of_self": relevant_reviews 
            }
            
            revised = agent.run_with_peer_context(instruction, 3, peer_context)
            revised_answers[agent.agent_id] = revised
            
        return revised_answers
