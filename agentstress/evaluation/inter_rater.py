import pandas as pd
from typing import List


class InterRater:
    """Calculates inter-rater reliability between judges."""

    @staticmethod
    def calculate_cohens_kappa(judge1_labels: List[str], judge2_labels: List[str]) -> float:
        """
        Calculates Cohen's Kappa for agreement between two judges' categorical labels.
        """
        if len(judge1_labels) != len(judge2_labels) or not judge1_labels:
            return 0.0

        df = pd.DataFrame({"j1": judge1_labels, "j2": judge2_labels})

        # Observed agreement
        po = (df["j1"] == df["j2"]).mean()

        # Expected agreement by chance
        pe_j1 = df["j1"].value_counts(normalize=True)
        pe_j2 = df["j2"].value_counts(normalize=True)

        pe = 0.0
        for label in set(judge1_labels).union(set(judge2_labels)):
            pe += pe_j1.get(label, 0) * pe_j2.get(label, 0)

        if pe == 1.0:
            return 1.0 if po == 1.0 else 0.0

        kappa = (po - pe) / (1 - pe)
        return max(0.0, kappa)


if __name__ == "__main__":
    j1 = ["NO_FAILURE", "INSTRUCTION_DRIFT", "NO_FAILURE", "TOOL_CALL_HALLUCINATION"]
    j2 = ["NO_FAILURE", "INSTRUCTION_DRIFT", "PARTIAL_FAILURE", "TOOL_CALL_HALLUCINATION"]
    print(InterRater.calculate_cohens_kappa(j1, j2))
