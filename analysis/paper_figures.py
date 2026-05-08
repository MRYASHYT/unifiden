import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

class PaperFigures:
    """
    Generates publication-quality figures for the research papers.
    """
    
    def __init__(self, output_dir: str = "paper/figures"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Set professional style
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})

    def plot_failure_rates(self, df: pd.DataFrame):
        """Generates a bar chart of failure rates by instruction type and architecture."""
        plt.figure(figsize=(10, 6))
        plot = sns.barplot(x="instruction_type", y="percentage", hue="architecture", data=df)
        plt.title("Failure Rates Across Instruction Types")
        plt.ylabel("Completion Score (%)")
        plt.xlabel("Instruction Clarity")
        plt.savefig(os.path.join(self.output_dir, "failure_rates.png"), dpi=300)
        plt.close()

    def plot_failure_mode_pie(self, df: pd.DataFrame):
        """Generates a pie chart for the overall failure mode distribution."""
        counts = df['failure_mode'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis"))
        plt.title("Overall Failure Mode Distribution")
        plt.savefig(os.path.join(self.output_dir, "failure_distribution.png"), dpi=300)
        plt.close()

    def plot_drift_histogram(self, df: pd.DataFrame):
        """Generates a histogram of the step at which drift occurred."""
        if 'drift_step' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(df['drift_step'], bins=15, kde=True, color="salmon")
            plt.title("Step Distribution of First Observable Failure")
            plt.xlabel("Execution Step Number")
            plt.savefig(os.path.join(self.output_dir, "drift_step_histogram.png"), dpi=300)
            plt.close()

if __name__ == "__main__":
    # Test plotting
    data = {
        "instruction_type": ["Clear", "Ambiguous", "Adversarial"] * 5,
        "percentage": [95, 80, 45, 98, 75, 40, 92, 85, 50, 96, 78, 42, 94, 82, 48],
        "architecture": ["ReAct"]*15,
        "failure_mode": ["NO_FAILURE"]*8 + ["INSTRUCTION_DRIFT"]*7,
        "drift_step": [1, 2, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 1, 2, 3]
    }
    df = pd.DataFrame(data)
    figures = PaperFigures()
    figures.plot_failure_rates(df)
    figures.plot_failure_mode_pie(df)
    figures.plot_drift_histogram(df)
    print(f"Figures saved to {figures.output_dir}")
