import json
import google.generativeai as genai
import os

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
        # Convert dicts to string for analysis
        r1_summary = json.dumps({k: v.get("output", "") for k, v in round1_answers.items()})
        r3_summary = json.dumps({k: v.get("response", "") for k, v in round3_answers.items()})
        
        prompt = f"""
        Identify if any incorrect information from one agent's Round 1 answer appeared in another agent's Round 3 answer.
        
        ROUND 1 PEER DATA:
        {r1_summary}
        
        ROUND 3 REVISED DATA:
        {r3_summary}
        
        Calculate the Contamination Index (0-10) where 10 means extensive propagation of hallucinations.
        Return only the number.
        """
        
        try:
            res = self.model.generate_content(prompt).text.strip()
            return float(res)
        except:
            return 0.0
