import asyncio
import os
import sys
import json
import dataclasses
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.agents.react_gpt import ReActGPTAgent
from agentstress.evaluation.rubric_engine import RubricEngine
from agentstress.evaluation.judge_gpt import GPTJudge
from agentstress.data.local_ledger import LocalLedger

load_dotenv()

async def run_agent_task(agent, task, rubric_engine, judge, ledger):
    """
    Executes a single agent task and records the result.
    """
    print(f"  Starting Task: {task['id']}")
    # agent.run is synchronous, run in executor
    loop = asyncio.get_event_loop()
    agent_res = await loop.run_in_executor(None, agent.run, task["instruction"], task["type"])
    
    score = rubric_engine.score_output(task["id"], agent.agent_id, agent_res.output)
    
    classification = judge.classify_failure(
        task["instruction"], task["type"], agent_res.output, score, [dataclasses.asdict(tc) for tc in agent_res.tool_calls]
    )
    
    final_data = {
        "task_id": task["id"],
        "agent_result": dataclasses.asdict(agent_res),
        "rubric_score": dataclasses.asdict(score),
        "failure_classification": dataclasses.asdict(classification)
    }
    ledger.record_entry(final_data)
    print(f"  Finished Task: {task['id']}")
    return final_data

async def run_batch(num_tasks=5):
    """
    Implements real async execution for a subset of tasks.
    """
    print(f"--- Initiating Async Batch ({num_tasks} tasks) ---")
    agent = ReActGPTAgent()
    rubric_engine = RubricEngine()
    judge = GPTJudge()
    ledger = LocalLedger()
    
    with open("tasks/clear_instructions.json", "r") as f:
        tasks = json.load(f)[:num_tasks]
        
    coroutines = [run_agent_task(agent, task, rubric_engine, judge, ledger) for task in tasks]
    results = await asyncio.gather(*coroutines)
    
    print(f"--- Batch Complete. {len(results)} tasks executed in parallel. ---")

if __name__ == "__main__":
    asyncio.run(run_batch())
