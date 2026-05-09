from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time


@dataclass
class ToolCall:
    step: int
    tool_name: str
    tool_input: str
    tool_output: str
    timestamp: float
    duration_ms: int


@dataclass
class AgentResult:
    agent_id: str
    architecture: str
    model: str
    instruction: str
    instruction_type: str
    output: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    total_steps: int = 0
    duration_seconds: float = 0.0
    completed: bool = False
    error: Optional[str] = None
    confidence_self_assessment: int = 0  # Agent rates its own confidence 0-10
    steps_completed: List[str] = field(default_factory=list)  # Agent lists every step it completed
    run_id: str = ""
    timestamp: float = field(default_factory=time.time)


class BaseAgent(ABC):

    def __init__(self, agent_id: str, model: str, temperature: float = 0.1):
        self.agent_id = agent_id
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def setup(self) -> None:
        """Initialize the agent — called once before any runs"""
        pass

    @abstractmethod
    def run(self, instruction: str, instruction_type: str) -> AgentResult:
        """Execute the agent on a task and return complete result"""
        pass

    @abstractmethod
    def run_with_peer_context(
        self, instruction: str, round_number: int, peer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run agent with awareness of peer responses (debate rounds 2-3)"""
        pass

    def validate_result(self, result: AgentResult) -> bool:
        """Validate result has all required fields"""
        required = ["output", "tool_calls", "completed", "agent_id"]
        return all(hasattr(result, field) for field in required)
