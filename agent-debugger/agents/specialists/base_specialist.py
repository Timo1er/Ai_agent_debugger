from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from llm.llm_provider import BaseLLMProvider

class BaseSpecialistAgent(ABC):
    """
    Classe de base pour tous les Agents Spécialistes du copilote de débogage.
    """
    def __init__(self, name: str, domain: str, client: Any, llm: BaseLLMProvider):
        self.name = name
        self.domain = domain
        self.client = client
        self.llm = llm

    @abstractmethod
    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Explore, stresse son domaine d'expertise et retourne la liste des bugs découverts.
        """
        pass