from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from debugger_client.unity_client import UnityDebuggerClient
from llm.llm_provider import BaseLLMProvider

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, client: UnityDebuggerClient, llm: BaseLLMProvider):
        self.name = name
        self.role = role
        self.client = client
        self.llm = llm
        self.history: List[Dict[str, Any]] = []

    def log(self, message: str):
        print(f"[{self.name} ({self.role})]: {message}")

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass