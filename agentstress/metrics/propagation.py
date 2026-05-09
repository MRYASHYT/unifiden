import json
import logging
from google import genai
from tenacity import retry, wait_exponential, stop_after_attempt
from agentstress.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropagationMetrics:
    """Tracks how hallucinations spread across the agent network."""

    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.model_name = Config.DEFAULT_GEMINI_MODEL

    def calculate_contamination_index(self, round1_answers: dict, round3_answers: dict) -> float:
        """
        Calculates Network Contamination Index.
        Compares false claims in R3 against R1 peer outputs.
        """
        if not round1_answers or not round3_answers:
            return 0.0

        # Convert dicts to string for analysis
        r1_summary = json.dumps(
            {k: v.get("output", "") for k, v in round1_answers.items()}, indent=2
        )
        r3_summary = json.dumps(
            {k: v.get("response", "") for k, v in round3_answers.items()}, indent=2
        )

        prompt = f"""
        Identify if any specific incorrect information or unique claims from one agent's Round 1 answer appeared in ANOTHER agent's Round 3 answer.
        
        ROUND 1 PEER DATA:
        {r1_summary}
        
        ROUND 3 REVISED DATA:
        {r3_summary}
        
        Calculate the Contamination Index (0-10) where:
        - 0: No propagation detected.
        - 5: One or two claims spread.
        - 10: Extensive propagation where one agent's errors corrupted the entire network.
        
        Return JSON only:
        {{
            "index": float,
            "propagated_claims": [
                {{"source": "agent_id", "target": "agent_id", "claim": "string"}}
            ],
            "reasoning": "string"
        }}
        """

        try:

            @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
            def invoke_model():
                return self.client.models.generate_content(model=self.model_name, contents=prompt)

            res = invoke_model()
            text = res.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            index = float(data.get("index", 0.0))
            logger.info(f"Contamination Index calculated: {index}")
            return index
        except Exception as e:
            logger.error(f"Error calculating contamination index: {str(e)}")
            return 0.0
