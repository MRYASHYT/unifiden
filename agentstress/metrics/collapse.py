class CollapseMetric:
    """
    Overconfidence Collapse Score (0-10)
    10 = frequently abandoned correct answers due to peer pressure.
    """

    @staticmethod
    def calculate(round1_correct: int, round3_abandoned: int) -> float:
        if round1_correct == 0:
            return 0.0
        return (round3_abandoned / round1_correct) * 10.0
