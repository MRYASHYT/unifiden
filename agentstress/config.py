import os
from dotenv import load_dotenv

# Load .env from project root
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
    DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"
    DEFAULT_GEMINI_MODEL = "models/gemini-1.5-flash"
    
    # Local AI (Ollama) - The $0 Cost Engine
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_LOCAL_MODEL = os.getenv("DEFAULT_LOCAL_MODEL", "llama3.1:8b")

    # Paths
    PROJECT_ROOT = base_dir
    TASKS_DIR = os.path.join(PROJECT_ROOT, "tasks")
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
    PAPER_DIR = os.path.join(PROJECT_ROOT, "paper")
    DATA_DIR = os.path.join(PROJECT_ROOT, "agentstress", "data")

    # Ledger
    LEDGER_FILE = os.path.join(DATA_DIR, "evaluation_ledger.jsonl")

    # Security
    KEY_PASS = os.getenv("AGENTSTRESS_KEY_PASS", "agentstress_secure_passphrase")

    # Framework Settings
    MOCK_MODE = os.getenv("AGENTSTRESS_MOCK", "False").lower() == "true"

    @classmethod
    def validate(cls):
        """Ensures critical settings are present."""
        # For the $0 Roadmap, we only strictly require GOOGLE_API_KEY (it's free)
        # and the KEY_PASS for security.
        missing = []
        if not cls.GOOGLE_API_KEY and not cls.MOCK_MODE:
            print("WARNING: GOOGLE_API_KEY not found. Free-tier metrics will fail.")
        
        if not cls.KEY_PASS:
            print("WARNING: AGENTSTRESS_KEY_PASS not set. Using default insecure passphrase.")


# Validate on import
Config.validate()
