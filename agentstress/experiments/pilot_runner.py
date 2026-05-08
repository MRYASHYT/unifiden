import os
import logging
from agentstress import logger
from agentstress.config import Config
from agentstress.agents.react_gpt import ReActGPTAgent
from agentstress.evaluation.judge_gpt import GPTJudge
from agentstress.data.local_ledger import LocalLedger

def run_pilot():
    """
    Standard pilot run for the AgentStress framework.
    Uses GPT-4o architecture and classifies failures.
    """
    logger.info("--- Starting AgentStress Pilot Run ---")
    
    # 1. Initialize Components
    agent = ReActGPTAgent()
    judge = GPTJudge()
    ledger = LocalLedger()
    
    # 2. Setup Task
    task_id = "clear_01"
    instruction = "Find the current stock price of NVIDIA and calculate the market cap if there are 2.46 billion shares outstanding."
    instruction_type = "clear"
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not Config.MOCK_MODE:
        logger.error("ERROR: OPENAI_API_KEY not found in .env. Please add it before running the pilot.")
        return

    # 3. Execution
    logger.info(f"Executing Agent ({agent.agent_id})...")
    agent_result = agent.run(instruction, instruction_type)
    
    if not agent_result.completed:
        logger.warning(f"Agent failed to complete task: {agent_result.error}")
    
    # 4. Evaluation
    logger.info("Scoring Output...")
    rubric = {"required_elements": ["NVIDIA stock price", "market cap calculation", "result > 2 trillion"]}
    rubric_score = judge.score_rubric(task_id, instruction, agent_result.output, rubric)
    
    logger.info("Classifying Failure Mode...")
    failure_info = judge.classify_failure(
        instruction, 
        instruction_type, 
        agent_result.output, 
        rubric_score, 
        [{"step": s.step, "tool": s.tool_name} for s in agent_result.tool_calls]
    )
    
    # 5. Result Aggregation
    result_record = {
        "run_id": agent_result.run_id,
        "agent_id": agent.agent_id,
        "task_id": task_id,
        "score_percent": rubric_score.percentage,
        "failure_mode": failure_info.failure_mode,
        "confidence": failure_info.confidence,
        "duration": agent_result.duration_seconds
    }
    
    # 6. Secure Logging
    logger.info("Recording Signed Result to Ledger...")
    signature = ledger.add_record(result_record)
    
    # 7. Final Summary
    logger.info("--- Pilot Run Complete ---")
    logger.info(f"Final Score: {rubric_score.percentage}%")
    logger.info(f"Failure Mode: {failure_info.failure_mode}")
    logger.info(f"Digital Signature: {signature[:16]}...")
    logger.info(f"Public Key for verification: {ledger.signer.public_key_path}")

if __name__ == "__main__":
    run_pilot()
