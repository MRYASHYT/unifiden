import os
import sys

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import dataclasses
from dotenv import load_dotenv
from agentstress.agents.react_gemini import ReActGeminiAgent
from agentstress.evaluation.rubric_engine import RubricEngine
from agentstress.evaluation.judge_gemini import GeminiJudge
from agentstress.data.local_ledger import LocalLedger

load_dotenv()


def run_pilot():
    """
    Orchestrates a complete, secure end-to-end evaluation cycle using Gemini.
    """
    print("--- Starting AgentStress Pilot Run (FULLY GEMINI POWERED) ---")

    # 1. Setup
    agent = ReActGeminiAgent()
    rubric_engine = RubricEngine()
    judge = GeminiJudge()
    ledger = LocalLedger()

    # 2. Task Definition
    instruction = "Find exactly 3 research papers on transformer architecture published in 2023. For each, provide the title and the primary author."
    instruction_type = "clear"
    task_id = "pilot_task_gemini_1"

    rubric_data = {
        "required_elements": ["Title", "Author", "2023"],
        "forbidden_elements": ["2017", "Attention is all you need"],
    }

    # 3. Execution
    print(f"Executing Agent ({agent.agent_id})...")
    agent_result = agent.run(instruction, instruction_type)

    if not agent_result.completed:
        print(f"Agent failed to complete task: {agent_result.error}")
        return

    # 4. Evaluation
    print("Scoring Output...")
    rubric_score = rubric_engine.score_output(
        task_id, agent.agent_id, agent_result.output, rubric_data
    )

    print("Classifying Failure Mode...")
    trace = [dataclasses.asdict(tc) for tc in agent_result.tool_calls]

    failure_info = judge.classify_failure(
        instruction, instruction_type, agent_result.output, rubric_score, trace
    )

    # 5. Secure Recording
    print("Recording Signed Result to Ledger...")
    final_report = {
        "task_id": task_id,
        "instruction": instruction,
        "agent_result": dataclasses.asdict(agent_result),
        "rubric_score": dataclasses.asdict(rubric_score),
        "failure_classification": dataclasses.asdict(failure_info),
    }

    signature = ledger.record_entry(final_report)

    print("\n--- Pilot Run Complete ---")
    print(f"Final Score: {rubric_score.percentage}%")
    print(f"Failure Mode: {failure_info.failure_mode}")
    print(f"Digital Signature: {signature[:16]}...")
    print(f"Public Key for verification: {ledger.signer.public_key_path}")


if __name__ == "__main__":
    # Check for API Keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in .env.")
    else:
        run_pilot()
