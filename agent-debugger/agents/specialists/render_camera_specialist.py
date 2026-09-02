from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class RenderCameraSpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : Rendu, Shaders, Caméras & Occlusion.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Rendu-Camera", "Rendering & Cameras", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"   [{self.name}] Analyse de la visibilité des caméras, lumières et matériaux...")
        bugs = []
        snap = context.get("snapshot")
        if snap and hasattr(snap, "warnings") and snap.warnings:
            for w in snap.warnings:
                if "ANOMALY_FOG" in w or "ANOMALY_LIGHT" in w:
                    bugs.append({
                        "specialist": self.name,
                        "domain": self.domain,
                        "severity": "HIGH",
                        "title": "Occultation visuelle anormale de la scène",
                        "description": w,
                        "reproduction": ["Charger la scène"],
                        "fix": "RenderSettings.fogDensity = 0.01f; // Restaurer densité standard"
                    })
        return bugs