import os
import sys
import json
import dataclasses
import time
from dotenv import load_dotenv

# Add project root to path
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
    
    # Initialize components
    agent = ReActGPTAgent()
    rubric_engine = RubricEngine()
    judge = GPTJudge()
    ledger = LocalLedger()
    
    # Load tasks
    tasks = []
    for filename in ["clear_instructions.json", "ambiguous_instructions.json", "adversarial_instructions.json"]:
        with open(os.path.join("tasks", filename), "r") as f:
            tasks.extend(json.load(f))
    
    print(f"Loaded {len(tasks)} tasks.")
    
    # Repetitions
    REPS = 10 # Spec requires 10
    
    results = []
    for i, task in enumerate(tasks):
        print(f"  [{i+1}/{len(tasks)}] Task: {task['instruction'][:50]}...")
        
        for r in range(REPS):
            print(f"    Rep {r+1}...")
            
            # 1. Run Agent
            agent_res = agent.run(task["instruction"], task["type"])
            
            # 2. Rubric Score
            score = rubric_engine.score_output(task["id"], agent.agent_id, agent_res.output)
            
            # 3. Final Classification
            classification = judge.classify_failure(
                task["instruction"], task["type"], agent_res.output, score, [dataclasses.asdict(tc) for tc in agent_res.tool_calls]
            )
            
            # 4. Record Result
            final_data = {
                "task_id": task["id"],
                "instruction_type": task["type"],
                "agent_result": dataclasses.asdict(agent_res),
                "rubric_score": dataclasses.asdict(score),
                "failure_classification": dataclasses.asdict(classification)
            }
            ledger.record_entry(final_data)
            results.append(final_data)
            
    print(f"=== EXPERIMENT COMPLETE. {len(results)} certifications recorded. ===")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
        print("Error: Required API keys not set in .env")
    else:
        run_paper1_experiment()
