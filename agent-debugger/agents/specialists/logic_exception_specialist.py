from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class LogicExceptionSpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : Exceptions C#, NullReferences & Intégrité Logique / UI.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Logique-Exceptions", "Logic & C# Exceptions", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"   [{self.name}] Traque des NullReferenceException et erreurs de script C#...")
        bugs = []
        snap = context.get("snapshot")
        if snap and hasattr(snap, "recentLogs") and snap.recentLogs:
            for log in snap.recentLogs:
                log_type = log.type if hasattr(log, "type") else log.get("type", "")
                log_msg = log.message if hasattr(log, "message") else log.get("message", "")
                if log_type in ["Error", "Exception"]:
                    bugs.append({
                        "specialist": self.name,
                        "domain": self.domain,
                        "severity": "HIGH",
                        "title": "Exception C# interceptée sur le moteur Unity",
                        "description": log_msg,
                        "reproduction": ["Exécuter la boucle de jeu"],
                        "fix": "if (target != null) { target.Execute(); }"
                    })
        return bugs