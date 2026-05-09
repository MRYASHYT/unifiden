import os
import sys
import json
import dataclasses
import time
import logging
from dotenv import load_dotenv
from agentstress import logger
from agentstress.config import Config

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.agents.react_gpt import ReActGPTAgent
from agentstress.agents.ollama_agent import OllamaAgent
from agentstress.evaluation.rubric_engine import RubricEngine
from agentstress.evaluation.judge_gpt import GPTJudge
from agentstress.evaluation.judge_gemini import GeminiJudge
from agentstress.data.local_ledger import LocalLedger

load_dotenv()


def run_paper1_experiment(use_local: bool = False):
    """
    Runs the 300-run experiment (30 tasks x 10 reps) for Paper 1 MVP.
    Now supports $0 local mode using Ollama and Gemini Free Tier.
    """
    logger.info("=== STARTING PAPER 1 EXPERIMENT (300 RUNS) ===")

    # 1. Initialize components based on mode
    if use_local:
        logger.info("MODE: LOCAL ($0 Cost Roadmap)")
        agent = OllamaAgent()
        # Use GeminiJudge because it has a massive free tier
        judge = GeminiJudge()
    else:
        logger.info("MODE: CLOUD (Paid APIs)")
        agent = ReActGPTAgent()
        judge = GPTJudge()
        
    rubric_engine = RubricEngine()
    ledger = LocalLedger()

    # 2. Load tasks
    tasks = []
    task_files = [
        "clear_instructions.json",
        "ambiguous_instructions.json",
        "adversarial_instructions.json",
    ]
    
    for filename in task_files:
        path = os.path.join(Config.TASKS_DIR, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                tasks.extend(json.load(f))

    logger.info(f"Loaded {len(tasks)} tasks.")

    # 3. Execution Loop
    REPS = 10  # Standard repetition count
    results_count = 0
    
    for i, task in enumerate(tasks):
        logger.info(f"  [{i+1}/{len(tasks)}] Task: {task['instruction'][:50]}...")

        for r in range(REPS):
            logger.info(f"    Rep {r+1}...")

            try:
                # 1. Run Agent
                agent_res = agent.run(task["instruction"], task["type"])

                # 2. Rubric Score
                score = rubric_engine.score_output(task["id"], agent.agent_id, agent_res.output)

                # 3. Final Classification
                classification = judge.classify_failure(
                    task["instruction"],
                    task["type"],
                    agent_res.output,
                    score,
                    [dataclasses.asdict(tc) for tc in agent_res.tool_calls],
                )

                # 4. Record Result
                final_data = {
                    "task_id": task["id"],
                    "instruction_type": task["type"],
                    "agent_result": dataclasses.asdict(agent_res),
                    "rubric_score": dataclasses.asdict(score),
                    "failure_classification": dataclasses.asdict(classification),
                }
                ledger.record_entry(final_data)
                results_count += 1
                
            except Exception as e:
                logger.error(f"    Critical error in execution: {str(e)}")
                continue

    logger.info(f"=== EXPERIMENT COMPLETE. {results_count} certifications recorded. ===")


if __name__ == "__main__":
    # Detect local mode from env or default to False
    local_mode = os.getenv("AGENTSTRESS_LOCAL", "False").lower() == "true"
    run_paper1_experiment(use_local=local_mode)
