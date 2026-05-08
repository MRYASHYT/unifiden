import argparse
from experiments.pilot_runner import run_pilot
from experiments.paper2_runner import run_paper2_experiment
from data.local_ledger import LocalLedger

def main():
    parser = argparse.ArgumentParser(description="Unifiden: AI Reliability Testing Framework")
    parser.add_argument("--mode", type=str, choices=["pilot", "experiment", "verify"], default="pilot", help="Mode to run")
    
    args = parser.parse_args()
    
    if args.mode == "pilot":
        run_pilot()
    elif args.mode == "experiment":
        run_paper2_experiment()
    elif args.mode == "verify":
        ledger = LocalLedger()
        if ledger.verify_ledger():
            print("SUCCESS: All certification records in the ledger are authentic and untampered.")
        else:
            print("CRITICAL ERROR: Tampering detected in the evaluation ledger!")

if __name__ == "__main__":
    main()
