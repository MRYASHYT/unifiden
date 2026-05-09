import os
import dataclasses
from typing import List, Dict, Any
from agentstress.agents.base_agent import BaseAgent
from agentstress.debate.round_1_runner import Round1Runner
from agentstress.debate.round_2_reviewer import Round2Reviewer
from agentstress.debate.round_3_reviser import Round3Reviser
from agentstress.debate.round_4_judge import Round4Judge


class DebateCoordinator:
    """
    Orchestrates the 4-round AgentStress debate protocol.
    1. Independent Execution
    2. Cross-Peer Review
    3. Revised Answers
    4. Final Judgment
    """

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
        self.round1 = Round1Runner(agents)
        self.round2 = Round2Reviewer(agents)
        self.round3 = Round3Reviser(agents)
        self.round4 = Round4Judge()

    def run_debate(self, instruction: str, instruction_type: str, rubric: dict) -> dict:
        print(f"--- Starting Debate on Task: {instruction[:50]}... ---")

        # Round 1: Independent Execution
        print("Round 1: Independent Execution...")
        round1_results = self.round1.run(instruction, instruction_type)

        # Round 2: Cross-Peer Review
        print("Round 2: Cross-Peer Review...")
        round2_results = self.round2.run(instruction, round1_results)

        # Round 3: Revised Answers
        print("Round 3: Revised Answers...")
        round3_results = self.round3.run(instruction, round1_results, round2_results)

        # Round 4: Final Judgment
        print("Round 4: Final Judgment...")
        final_judgment = self.round4.run(
            instruction, instruction_type, round1_results, round2_results, round3_results, rubric
        )

        return {
            "instruction": instruction,
            "instruction_type": instruction_type,
            "round1": round1_results,
            "round2": round2_results,
            "round3": round3_results,
            "final_judgment": final_judgment,
        }
