import pandas as pd
import numpy as np
from scipy import stats
import logging
from agentstress import logger

class AgentStressStats:
    """
    Industrial statistics engine for AI reliability data.
    Provides significance testing and performance distribution analysis.
    """
    
    def __init__(self):
        self.logger = logger

    def calculate_summary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes mean, std, and count per architecture."""
        return df.groupby('architecture')['percentage'].agg(['mean', 'std', 'count']).reset_index()

    def compare_instruction_types(self, df: pd.DataFrame, type1: str, type2: str) -> dict:
        """Performs T-Test between two instruction clarity levels."""
        group1 = df[df['instruction_type'] == type1]['percentage']
        group2 = df[df['instruction_type'] == type2]['percentage']
        
        if len(group1) < 2 or len(group2) < 2:
            return {"error": "Insufficient data for T-Test"}
            
        t_stat, p_val = stats.ttest_ind(group1, group2)
        return {
            "t_statistic": t_stat,
            "p_value": p_val,
            "significant": p_val < 0.05
        }

    def detect_outliers(self, df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """Identifies runs with duration or score anomalies."""
        z_scores = np.abs(stats.zscore(df['duration_seconds']))
        return df[z_scores > threshold]
