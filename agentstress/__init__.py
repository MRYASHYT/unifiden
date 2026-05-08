import logging
import sys
from agentstress.config import Config

def setup_logging():
    """
    Initializes a standardized logging system for the AgentStress framework.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("agentstress.log")
        ]
    )

setup_logging()
logger = logging.getLogger("agentstress")
