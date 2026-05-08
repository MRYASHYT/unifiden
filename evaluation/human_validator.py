import json
import pandas as pd
import os
from typing import List, Dict
from evaluation.inter_rater import InterRater

class HumanValidator:
    """
    Interface for human-in-the-loop validation of AI judgments.
    Compares human scores to automated scores to report Inter-Rater Reliability.
    """
    
    def __init__(self, ledger_file: str = "data/evaluation_ledger.jsonl"):
        self.ledger_file = ledger_file

    def sample_for_validation(self, n: int = 50) -> List[Dict]:
        """Samples random runs from the ledger for human review."""
        runs = []
        if not os.path.exists(self.ledger_file): return []
        with open(self.ledger_file, "r") as f:
            for line in f:
                runs.append(json.loads(line))
        return runs[:n]

    def record_human_score(self, run_id: str, human_failure_mode: str, human_score: int):
        """Appends human validation results to a CSV."""
        val_data = {
            "run_id": run_id,
            "human_failure_mode": human_failure_mode,
            "human_score": human_score
        }
        df = pd.DataFrame([val_data])
        res_dir = "results"
        os.makedirs(res_dir, exist_ok=True)
        df.to_csv(os.path.join(res_dir, "human_validation.csv"), mode='a', header=not os.path.exists(os.path.join(res_dir, "human_validation.csv")), index=False)

    def calculate_agreement(self) -> float:
        """
        Calculates the agreement percentage (Cohen's Kappa) between AI and Human labels.
        """
        human_csv = "results/human_validation.csv"
        if not os.path.exists(human_csv):
            return 0.0
            
        h_df = pd.read_csv(human_csv)
        
        # Load AI results from ledger
        ai_labels = []
        human_labels = []
        
        runs = self.sample_for_validation(1000)
        ai_dict = {r["data"].get("agent_result", {}).get("run_id"): r["data"].get("failure_classification", {}).get("failure_mode") for r in runs}
        
        for _, row in h_df.iterrows():
            run_id = str(row["run_id"])
            if run_id in ai_dict:
                ai_labels.append(ai_dict[run_id])
                human_labels.append(row["human_failure_mode"])
                
        return InterRater.calculate_cohens_kappa(ai_labels, human_labels)

if __name__ == "__main__":
    validator = HumanValidator()
    print("Human Validation Module Initialized.")
