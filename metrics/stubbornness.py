class StubbornnessMetric:
    """
    10 = never changed wrong answers despite correct peer evidence.
    0 = updated all wrong answers when peers provided corrections.
    """
    @staticmethod
    def calculate(round1_wrong: int, round3_still_wrong: int) -> float:
        if round1_wrong == 0: return 0.0
        return (round3_still_wrong / round1_wrong) * 10.0
