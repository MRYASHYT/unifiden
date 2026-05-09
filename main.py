import argparse
import os
import logging
from agentstress import logger


def main():
    parser = argparse.ArgumentParser(description="AgentStress: AI Reliability Testing Framework")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["pilot", "experiment", "verify"],
        default="pilot",
        help="Mode to run",
    )
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API calls")
    parser.add_argument("--local", action="store_true", help="Use local Ollama for the agent")

    args = parser.parse_args()

    if args.mock:
        logger.info("--- RUNNING IN MOCK MODE ---")
        os.environ["AGENTSTRESS_MOCK"] = "True"

    if args.mode == "pilot":
        from agentstress.experiments.pilot_runner import run_pilot
        run_pilot(use_local=args.local)
    elif args.mode == "experiment":
        from agentstress.experiments.paper2_runner import run_paper2_experiment
        run_paper2_experiment()
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
