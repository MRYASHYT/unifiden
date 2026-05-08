import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any

class DebateHelper:
    @staticmethod
    def run_debate_round(llm, agent_id: str, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        if round_number == 2:
            prompt = ChatPromptTemplate.from_template("""
            Task: {instruction}
            You are reviewing the work of other agents. Be harsh and critical.
            Peer Answers: {peer_data}
            
            For each peer, provide:
            1. List of correct elements.
            2. List of missing or wrong elements.
            3. Completeness score (0-10).
            4. Accuracy score (0-10).
            """)
            response = llm.invoke(prompt.format(instruction=instruction, peer_data=json.dumps(peer_data)))
            return {"agent_id": agent_id, "round": 2, "response": response.content}
            
        elif round_number == 3:
            prompt = ChatPromptTemplate.from_template("""
            Task: {instruction}
            Your original answer: {round1_own}
            Peer reviews of all answers: {peer_reviews}
            
            Based on the reviews, provide your final, best, and most accurate answer.
            Only change your original answer if you are convinced the peer feedback is correct.
            """)
            response = llm.invoke(prompt.format(
                instruction=instruction, 
                round1_own=json.dumps(peer_data.get("round1_own")), 
                peer_reviews=json.dumps(peer_data.get("peer_reviews"))
            ))
            return {"agent_id": agent_id, "round": 3, "response": response.content}
        
        return {"agent_id": agent_id, "round": round_number, "response": "Invalid round"}
