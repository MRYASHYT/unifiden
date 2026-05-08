import os
import time
import uuid
import json
from typing import List, Dict, Any, Optional, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from agents.base_agent import BaseAgent, AgentResult, ToolCall

load_dotenv()

class GraphState(TypedDict):
    instruction: str
    search_data: str
    draft: str
    verification: str
    final_output: str
    tool_calls: List[Any]

class MultiAgentGraphAgent(BaseAgent):
    """
    Agent 5: Multi-Agent Graph + GPT-4o
    Architecture: SearchNode -> SynthesisNode -> VerificationNode -> MergerNode.
    """
    
    def __init__(self, agent_id: str = "agent_5_multi_agent_graph", model: str = "gpt-4o", temperature: float = 0.1):
        super().__init__(agent_id, model, temperature)
        self.llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        self.search_tool = DuckDuckGoSearchRun()

    def setup(self) -> None:
        pass

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        def search_node(state: GraphState):
            query = self.llm.invoke(f"Generate search query for: {state['instruction']}").content
            res = self.search_tool.run(query)
            tc = ToolCall(step=1, tool_name="Search", tool_input=query, tool_output=res, timestamp=time.time(), duration_ms=0)
            return {"search_data": res, "tool_calls": state.get("tool_calls", []) + [tc]}

        def synthesis_node(state: GraphState):
            res = self.llm.invoke(f"Task: {state['instruction']}\nData: {state['search_data']}\nWrite a detailed answer.").content
            return {"draft": res}

        def verification_node(state: GraphState):
            res = self.llm.invoke(f"Fact-check this answer against the task: {state['instruction']}\nAnswer: {state['draft']}\nIdentify errors.").content
            return {"verification": res}

        def merger_node(state: GraphState):
            res = self.llm.invoke(f"Original: {state['draft']}\nErrors Found: {state['verification']}\nProduce final verified answer.").content
            return {"final_output": res}

        workflow.add_node("search", search_node)
        workflow.add_node("synthesis", synthesis_node)
        workflow.add_node("verification", verification_node)
        workflow.add_node("merger", merger_node)

        workflow.set_entry_point("search")
        workflow.add_edge("search", "synthesis")
        workflow.add_edge("synthesis", "verification")
        workflow.add_edge("verification", "merger")
        workflow.add_edge("merger", END)

        return workflow.compile()

    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        try:
            app = self._build_graph()
            result = app.invoke({"instruction": instruction, "tool_calls": []})
            
            duration = time.time() - start_time
            assess = self.llm.invoke(f"Rate confidence (0-10) for: {instruction}. Return number only.").content
            try: conf = int(assess.strip())
            except: conf = 9

            return AgentResult(
                agent_id=self.agent_id, architecture="Multi-Agent Graph", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output=result["final_output"],
                tool_calls=result["tool_calls"], total_steps=len(result["tool_calls"]) + 3,
                duration_seconds=duration, completed=True, run_id=run_id,
                confidence_self_assessment=conf, steps_completed=["Search", "Synthesis", "Verification", "Merger"]
            )
            
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id, architecture="Multi-Agent Graph", model=self.model,
                instruction=instruction, instruction_type=instruction_type, output="",
                completed=False, error=str(e), duration_seconds=time.time()-start_time, run_id=run_id
            )

    def run_with_peer_context(self, instruction: str, round_number: int, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        from debate.debate_helper import DebateHelper
        return DebateHelper.run_debate_round(self.llm, self.agent_id, instruction, round_number, peer_data)
