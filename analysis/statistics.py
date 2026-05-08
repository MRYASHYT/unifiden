import pandas as pd
import numpy as np
from scipy import stats

class UnifidenStats:
    """
    Handles statistical computations for research papers.
    Includes T-tests, ANOVA, and Effect Size (Cohen's d).
    """
    
    @staticmethod
    def compare_instruction_types(df: pd.DataFrame, type1: str, type2: str, metric: str = "percentage"):
        """Performs T-test between two instruction types."""
        group1 = df[df['instruction_type'] == type1][metric]
        group2 = df[df['instruction_type'] == type2][metric]
        
        t_stat, p_val = stats.ttest_ind(group1, group2)
        
        # Calculate Cohen's d for effect size
        d = (np.mean(group1) - np.mean(group2)) / (np.sqrt((np.std(group1)**2 + np.std(group2)**2) / 2))
        
        return {
            "t_statistic": t_stat,
            "p_value": p_val,
            "cohens_d": d,
            "significant": p_val < 0.05
        }

    @staticmethod
    def anova_across_architectures(df: pd.DataFrame, metric: str = "percentage"):
        """Performs One-way ANOVA across all architectures."""
        groups = [group[metric].values for name, group in df.groupby('architecture')]
        f_stat, p_val = stats.f_oneway(*groups)
        
        return {
            "f_statistic": f_stat,
            "p_value": p_val,
            "significant": p_val < 0.05
        }

    @staticmethod
    def failure_mode_distribution(df: pd.DataFrame):
        """Calculates the distribution of failure modes."""
        return df['failure_mode'].value_counts(normalize=True).to_dict()

if __name__ == "__main__":
    # Example usage with mock data
    data = {
        "instruction_type": ["clear"]*10 + ["adversarial"]*10,
        "percentage": np.random.normal(90, 5, 10).tolist() + np.random.normal(40, 10, 10).tolist(),
        "architecture": ["ReAct"]*20,
        "failure_mode": ["NO_FAILURE"]*12 + ["INSTRUCTION_DRIFT"]*8
    }
    df = pd.DataFrame(data)
    stats_engine = UnifidenStats()
    print(stats_engine.compare_instruction_types(df, "clear", "adversarial"))
