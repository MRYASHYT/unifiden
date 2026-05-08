import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.react_gpt import ReActGPTAgent
from evaluation.rubric_engine import RubricEngine
from evaluation.judge_gpt import GPTJudge
from data.local_ledger import LocalLedger

load_dotenv()

def run_paper1_experiment():
    """
    Runs the 300-run experiment (30 tasks x 10 reps) for Paper 1 MVP.
    """
    print("=== STARTING PAPER 1 EXPERIMENT (300 RUNS) ===")
    
    # Use ReActGPTAgent for Paper 1 MVP
    agent = ReActGPTAgent()
    rubric_engine = RubricEngine()
    judge = GPTJudge()
    ledger = LocalLedger()
    
    # In a real run, loop over clear_instructions.json etc. 
    # For now, this is the scaffolded runner structure for paper 1.
    print("Mocking 300 runs to save API costs... (use batch_runner for real parallel runs)")
    
    print("=== EXPERIMENT COMPLETE ===")

if __name__ == "__main__":
    run_paper1_experiment()
