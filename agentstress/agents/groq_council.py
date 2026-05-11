import os
import json
import time
from typing import List, Dict, Any
from groq import Groq

class GroqCouncil:
    """
    A multi-model council debate engine powered by Groq.
    Implements a 4-step debate methodology (Action, Critique, Revision, Judgment).
    """
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.models = [
            "llama-3.3-70b-versatile",    # The Leader
            "llama-3.1-8b-instant",       # The Fast Reviewer
            "mixtral-8x7b-32768",         # The Logical Critic
            "llama3-70b-8192",            # The Senior Judge
            "llama3-8b-8192"              # The Consensus Builder
        ]

    def ask(self, model: str, role: str, instruction: str, context: str = "") -> str:
        """Gets an answer or critique from a specific model."""
        try:
            res = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are the {role} in an AI Council. Be objective and rigorous."},
                    {"role": "user", "content": f"Task: {instruction}\nContext: {context}"}
                ],
                model=model,
                temperature=0.2,
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"Error from {model}: {str(e)}"

    def run_debate(self, instruction: str) -> Dict[str, str]:
        """Runs the complete debate round."""
        ans1 = self.ask(self.models[0], "Primary Actor", instruction)
        crit = self.ask(self.models[1], "Critical Reviewer", instruction, f"Initial Answer: {ans1}")
        ans2 = self.ask(self.models[2], "Revision Specialist", instruction, f"Original: {ans1}\nCritique: {crit}")
        final = self.ask(self.models[3], "Senior Judge", instruction, f"Initial: {ans1}\nRevised: {ans2}")
        
        return {
            "initial_answer": ans1,
            "critique": crit,
            "revised_answer": ans2,
            "final_judgment": final
        }
