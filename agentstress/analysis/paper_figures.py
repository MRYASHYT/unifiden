import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os


class PaperFigures:
    """
    Generates publication-quality figures for the research papers.
    Uses the real experimental results generated in the results/ folder.
    """

    def __init__(self, output_dir: str = "paper/figures"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Set professional style
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({"font.size": 12, "font.family": "serif"})

    def plot_failure_rates(self, df: pd.DataFrame):
        """Generates a bar chart of completion scores by instruction type and architecture."""
        plt.figure(figsize=(10, 6))
        plot = sns.barplot(
            x="instruction_type", y="percentage", hue="architecture", data=df, palette="viridis"
        )
        plt.title("Mean Completion Score Across Instruction Clarity")
        plt.ylabel("Score (%)")
        plt.xlabel("Instruction Type")
        plt.savefig(os.path.join(self.output_dir, "failure_rates.png"), dpi=300)
        plt.close()

    def plot_failure_mode_pie(self, df: pd.DataFrame):
        """Generates a pie chart for the overall failure mode distribution."""
        counts = df["failure_mode"].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(
            counts,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("magma"),
        )
        plt.title("Overall Failure Mode Distribution")
        plt.savefig(os.path.join(self.output_dir, "failure_distribution.png"), dpi=300)
        plt.close()


if __name__ == "__main__":
    # Load real results
    res_path = "results/paper1_results.csv"
    if os.path.exists(res_path):
        df = pd.read_csv(res_path)
        figures = PaperFigures()
        figures.plot_failure_rates(df)
        figures.plot_failure_mode_pie(df)
        print(f"Publication figures successfully generated in {figures.output_dir}")
    else:
        print("Error: results/paper1_results.csv not found. Run the experimental script first.")
