import json
import google.generativeai as genai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropagationMetrics:
    """Tracks how hallucinations spread across the agent network."""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

    def calculate_contamination_index(self, round1_answers: dict, round3_answers: dict) -> float:
        """
        Calculates Network Contamination Index.
        Compares false claims in R3 against R1 peer outputs.
        """
        if not round1_answers or not round3_answers:
            return 0.0

        # Convert dicts to string for analysis
        r1_summary = json.dumps({k: v.get("output", "") for k, v in round1_answers.items()}, indent=2)
        r3_summary = json.dumps({k: v.get("response", "") for k, v in round3_answers.items()}, indent=2)
        
        prompt = f"""
        Identify if any specific incorrect information or unique claims from one agent's Round 1 answer appeared in ANOTHER agent's Round 3 answer.
        
        ROUND 1 PEER DATA:
        {r1_summary}
        
        ROUND 3 REVISED DATA:
        {r3_summary}
        
        Calculate the Contamination Index (0-10) where:
        - 0: No propagation detected.
        - 5: One or two claims spread.
        - 10: Extensive propagation where one agent's errors corrupted the entire network.
        
        Return JSON only:
        {{
            "index": float,
            "propagated_claims": [
                {{"source": "agent_id", "target": "agent_id", "claim": "string"}}
            ],
            "reasoning": "string"
        }}
        """
        
        try:
            res = self.model.generate_content(prompt).text
            if "```json" in res: res = res.split("```json")[1].split("```")[0].strip()
            elif "```" in res: res = res.split("```")[1].split("```")[0].strip()
            
            data = json.loads(res)
            index = float(data.get("index", 0.0))
            logger.info(f"Contamination Index calculated: {index}")
            return index
        except Exception as e:
            logger.error(f"Error calculating contamination index: {str(e)}")
            return 0.0
