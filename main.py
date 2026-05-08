import argparse
import os
import logging
from agentstress import logger
from agentstress.experiments.pilot_runner import run_pilot
from agentstress.experiments.paper2_runner import run_paper2_experiment
from agentstress.data.local_ledger import LocalLedger

def main():
    parser = argparse.ArgumentParser(description="AgentStress: AI Reliability Testing Framework")
    parser.add_argument("--mode", type=str, choices=["pilot", "experiment", "verify"], default="pilot", help="Mode to run")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API calls")
    
    args = parser.parse_args()
    
    if args.mock:
        logger.info("--- RUNNING IN MOCK MODE ---")
        os.environ["AGENTSTRESS_MOCK"] = "True"
    
    if args.mode == "pilot":
        run_pilot()
    elif args.mode == "experiment":
        run_paper2_experiment()
    elif args.mode == "verify":
        ledger = LocalLedger()
        if ledger.verify_ledger():
            logger.info("SUCCESS: All certification records in the ledger are authentic and untampered.")
        else:
            logger.error("CRITICAL ERROR: Tampering detected in the evaluation ledger!")

if __name__ == "__main__":
    main()
