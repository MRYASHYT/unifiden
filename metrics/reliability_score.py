from typing import Dict, Any

class ReliabilityScore:
    """
    Combines various metrics into a single reliability score (0-100).
    """
    @staticmethod
    def calculate(
        completion_rate: bool,
        completeness_score: float,
        drift_score: float,
        stubbornness: float = 0.0,
        collapse: float = 0.0
    ) -> float:
        # Base score from completeness (0-10 -> 0-100)
        score = completeness_score * 10.0
        
        # Penalties
        score -= (drift_score * 5.0)
        score -= (stubbornness * 2.0)
        score -= (collapse * 5.0)
        
        # Binary completion bonus/penalty
        if not completion_rate:
            score *= 0.8
            
        return max(0.0, min(100.0, score))
