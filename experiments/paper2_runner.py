import os
from dotenv import load_dotenv
from agents.react_gpt import ReActGPTAgent
from agents.plan_execute_gpt import PlanExecuteGPTAgent
from agents.reflexion_gpt import ReflexionGPTAgent
from agents.react_claude import ReActClaudeAgent
from agents.multi_agent_graph import MultiAgentGraphAgent
from debate.debate_coordinator import DebateCoordinator
from data.local_ledger import LocalLedger

load_dotenv()

def run_paper2_experiment():
    """
    Runs the full multi-agent debate experiment (Paper 2).
    """
    print("=== STARTING PAPER 2 EXPERIMENT: MULTI-AGENT DEBATE ===")
    
    # 1. Initialize Agents
    agents = [
        ReActGPTAgent(),
        PlanExecuteGPTAgent(),
        ReflexionGPTAgent(),
        ReActClaudeAgent(),
        MultiAgentGraphAgent()
    ]
    
    # 2. Setup Coordinator
    coordinator = DebateCoordinator(agents)
    ledger = LocalLedger()
    
    # 3. Task Selection (Example)
    instruction = "Analyze the impact of transformer scaling laws on large language model efficiency between 2020 and 2024. Provide 5 key findings with citations."
    instruction_type = "adversarial" # Complex task
    
    rubric = {
        "required_elements": ["Scaling Laws", "Efficiency", "2020", "2024", "Citations", "5 findings"],
        "forbidden_elements": ["Pre-2020 data exclusively"]
    }
    
    # 4. Run Debate
    debate_results = coordinator.run_debate(instruction, instruction_type, rubric)
    
    # 5. Record Results
    print("Experiment complete. Recording to secure ledger...")
    ledger.record_entry(debate_results)
    
    print("\n=== EXPERIMENT COMPLETE ===")
    print(f"Results recorded in {ledger.ledger_file}")
    print(f"Verification Status: {ledger.verify_ledger()}")

if __name__ == "__main__":
    run_paper2_experiment()
