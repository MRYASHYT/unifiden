import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import uuid
import json
import dataclasses
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from agentstress.security.crypto_signer import CryptoSigner
from agentstress.evaluation.rubric_engine import RubricEngine
from agentstress.data.local_ledger import LocalLedger

load_dotenv()

# Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SimpleGeminiAgent:
    """A lightweight ReAct-style agent using the native Gemini SDK."""
    def __init__(self, agent_id="gemini_native_pilot"):
        self.agent_id = agent_id
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

    def run(self, instruction: str):
        print(f"  Agent {self.agent_id} is thinking...")
        start_time = time.time()
        
        prompt = f"""
        Task: {instruction}
        System: You are an AI researcher. Use a step-by-step reasoning approach.
        1. Search for relevant papers from 2023.
        2. Verify authors and titles.
        3. Provide exactly 3 papers.
        
        Return your final answer.
        """
        
        response = self.model.generate_content(prompt)
        duration = time.time() - start_time
        
        return {
            "output": response.text,
            "duration": duration,
            "agent_id": self.agent_id
        }

class SimpleGeminiJudge:
    """A lightweight Judge using the native Gemini SDK."""
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-flash-latest')

    def classify(self, instruction, output, rubric):
        print("  Judge is evaluating...")
        prompt = f"""
        Instruction: {instruction}
        Agent Output: {output}
        Rubric: {json.dumps(rubric)}
        
        Classify the failure mode (or NO_FAILURE) based on the taxonomy:
        NO_FAILURE, INSTRUCTION_DRIFT, PREMATURE_TERMINATION, TOOL_CALL_HALLUCINATION.
        
        Return JSON with: failure_mode, confidence (0-10), reasoning.
        """
        response = self.model.generate_content(prompt)
        content = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(content)

def run_native_pilot():
    print("--- Starting AgentStress Native Gemini Pilot ---")
    
    # 1. Setup
    agent = SimpleGeminiAgent()
    judge = SimpleGeminiJudge()
    rubric_engine = RubricEngine()
    ledger = LocalLedger()
    
    instruction = "Find 3 research papers on transformer architecture published in 2023. Provide title and primary author."
    rubric_data = {"required_elements": ["Title", "Author", "2023"]}
    
    # 2. Agent Run
    res = agent.run(instruction)
    
    # 3. Rubric Score
    score = rubric_engine.score_output("pilot_task", agent.agent_id, res["output"], rubric_data)
    
    # 4. Judgment
    judgment = judge.classify(instruction, res["output"], rubric_data)
    
    # 5. Record & Sign
    report = {
        "agent_id": agent.agent_id,
        "instruction": instruction,
        "output": res["output"],
        "score": score.percentage,
        "judgment": judgment
    }
    
    sig = ledger.record_entry(report)
    
    print("\n--- Pilot Run Complete ---")
    print(f"Final Score: {score.percentage}%")
    print(f"Failure Mode: {judgment['failure_mode']}")
    print(f"Digital Signature: {sig[:16]}...")
    print(f"Ledger Verified: {ledger.verify_ledger()}")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not set.")
    else:
        run_native_pilot()
