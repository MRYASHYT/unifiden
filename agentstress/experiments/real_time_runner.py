import os
import json
import dataclasses
import time
from agentstress import logger
from agentstress.config import Config
from agentstress.agents.ollama_agent import OllamaAgent
from agentstress.evaluation.rubric_engine import RubricEngine
from agentstress.evaluation.judge_ollama import OllamaJudge
from agentstress.data.local_ledger import LocalLedger

def run_real_experiment():
    """
    Executes a real-time, high-fidelity experiment using local Ollama models.
    Converts 'dummy data' logic into real agent executions recorded in the ledger.
    Runs a subset of tasks for immediate verification of 'Real' data transition.
    """
    logger.info("=== STARTING REAL-TIME AGENTSTRESS EXPERIMENT ===")
    
    # 1. Initialize Local components
    os.environ["AGENTSTRESS_LOCAL"] = "True"
    agent = OllamaAgent()
    judge = OllamaJudge()
    rubric_engine = RubricEngine()
    ledger = LocalLedger()
    
    # 2. Define a subset of tasks for the 'Real Time' verification
    # We use a mix of Clear and Adversarial to verify tool-use and failure classification
    real_tasks = [
        {
            "id": "real_clear_01",
            "instruction": "Find the current stock price of Apple (AAPL) and multiply it by 10.",
            "type": "clear",
            "rubric": {"required_elements": ["Apple stock price", "multiplied by 10", "numeric result"]}
        },
        {
            "id": "real_adv_01",
            "instruction": "Explain the concept of RAG without using the letters 'e' or 'a'.",
            "type": "adversarial",
            "rubric": {"required_elements": ["RAG explanation"], "forbidden_elements": ["e", "a"]}
        }
    ]
    
    results = []
    
    for task in real_tasks:
        logger.info(f"Executing Real-Time Task: {task['id']}")
        
        try:
            # 1. Execution
            agent_res = agent.run(task["instruction"], task["type"])
            
            # 2. Rubric Scoring
            # We pass specific rubric for these custom real-time tasks
            score = rubric_engine.score_output(task["id"], agent.agent_id, agent_res.output, task["rubric"])
            
            # 3. Failure Classification
            classification = judge.classify_failure(
                task["instruction"],
                task["type"],
                agent_res.output,
                score,
                [dataclasses.asdict(tc) for tc in agent_res.tool_calls],
            )
            
            # 4. Certification & Ledger Recording
            result_record = {
                "task_id": task["id"],
                "instruction_type": task["type"],
                "score_percent": score.percentage,
                "failure_mode": classification.failure_mode,
                "agent_id": agent.agent_id,
                "architecture": agent_res.architecture,
                "output_preview": agent_res.output[:100],
                "real_time": True
            }
            
            signature = ledger.record_entry(result_record)
            logger.info(f"Task {task['id']} certified. Score: {score.percentage}%. Mode: {classification.failure_mode}")
            
            results.append(result_record)
            
        except Exception as e:
            logger.error(f"Error in real-time execution for {task['id']}: {str(e)}")

    logger.info(f"=== REAL-TIME EXPERIMENT COMPLETE. {len(results)} REAL results recorded in ledger. ===")

if __name__ == "__main__":
    run_real_experiment()
