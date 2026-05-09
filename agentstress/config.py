import os
from dotenv import load_dotenv

# Load .env from project root
# Since this file is in agentstress/config.py, project root is one level up
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))


class Config:
    """
    Centralized configuration for the AgentStress framework.
    Industry standard practice to avoid scattered os.getenv calls.
    """

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Model Settings
    DEFAULT_GPT_MODEL = "gpt-4o"
    DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-latest"
    DEFAULT_GEMINI_MODEL = "models/gemini-flash-latest"

    # Paths
    PROJECT_ROOT = base_dir
    TASKS_DIR = os.path.join(PROJECT_ROOT, "tasks")
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
    PAPER_DIR = os.path.join(PROJECT_ROOT, "paper")
    DATA_DIR = os.path.join(PROJECT_ROOT, "agentstress", "data")

    # Ledger
    LEDGER_FILE = os.path.join(DATA_DIR, "evaluation_ledger.jsonl")

    # Security
    KEY_PASS = os.getenv("AGENTSTRESS_KEY_PASS")

    # Framework Settings
    MOCK_MODE = os.getenv("AGENTSTRESS_MOCK", "False").lower() == "true"

    @classmethod
    def validate(cls):
        """Ensures critical settings are present."""
        missing = []
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.KEY_PASS:
            missing.append("AGENTSTRESS_KEY_PASS")

        if missing and not cls.MOCK_MODE:
            error_msg = (
                f"FATAL ERROR: Missing critical environment variables: {', '.join(missing)}\n"
            )
            error_msg += (
                "Enterprise deployment requires explicit configuration. Set them in the .env file."
            )
            raise ValueError(error_msg)


# Validate on import
Config.validate()
