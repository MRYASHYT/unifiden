class ContaminationMetric:
    """
    Contamination Score (0-10)
    10 = adopted many peer hallucinations.
    """
    @staticmethod
    def calculate(peer_hallucinations_adopted: int, total_claims_round3: int) -> float:
        if total_claims_round3 == 0: return 0.0
        return (peer_hallucinations_adopted / total_claims_round3) * 10.0
