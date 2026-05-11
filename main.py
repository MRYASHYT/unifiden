import argparse
import os
import logging
from agentstress import logger


def main():
    parser = argparse.ArgumentParser(description="AgentStress: AI Reliability Testing Framework")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["pilot", "experiment", "verify", "council", "certify"],
        default="pilot",
        help="Mode to run",
    )
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API calls")
    parser.add_argument("--local", action="store_true", help="Use local Ollama for the agent")
    parser.add_argument("--free", action="store_true", help="Use Gemini Free Tier for $0 cost without needing Ollama")
    parser.add_argument("--groq", action="store_true", help="Use Groq (Llama 3) for ultra-fast experiments")

    args = parser.parse_args()

    if args.mock:
        logger.info("--- RUNNING IN MOCK MODE ---")
        os.environ["AGENTSTRESS_MOCK"] = "True"

    if args.mode == "pilot":
        from agentstress.experiments.pilot_runner import run_pilot
        run_pilot(use_local=args.local)
    elif args.mode == "experiment":
        from agentstress.experiments.paper1_runner import run_paper1_experiment
        run_paper1_experiment(use_local=args.local, use_free_cloud=args.free, use_groq=args.groq)
    elif args.mode == "council":
        from agentstress.config import Config
        from agentstress.agents.groq_council import GroqCouncil
        from tqdm.auto import tqdm
        logger.info("--- STARTING MULTI-MODEL COUNCIL DEBATE ---")
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            logger.error("GROQ_API_KEY not found. Required for council mode.")
            return
        council = GroqCouncil(groq_key)
        # Placeholder for task execution loop - in practice, this would run over the standard tasks
        logger.info("Council Debate initialized. (Add tasks to run full batch)")
    elif args.mode == "certify":
        from agentstress.evaluation.certification_judge import CertificationJudge
        logger.info("--- STARTING GLOBAL COMPLIANCE CERTIFICATION ---")
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            logger.error("GROQ_API_KEY not found. Required for certification mode.")
            return
        judge = CertificationJudge(groq_key)
        logger.info("Compliance Engine initialized and ready to audit.")
    elif args.mode == "verify":
        from agentstress.data.local_ledger import LocalLedger
        ledger = LocalLedger()
        if ledger.verify_ledger():
            logger.info(
                "SUCCESS: All certification records in the ledger are authentic and untampered."
            )
        else:
            logger.error("CRITICAL ERROR: Tampering detected in the evaluation ledger!")


if __name__ == "__main__":
    main()
