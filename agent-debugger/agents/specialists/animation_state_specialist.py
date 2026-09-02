from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class AnimationStateSpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : State Machines, Animators, Root Motion & Transitions.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Animation-State", "Animation & State Machines", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"   [{self.name}] Analyse des State Machines d'animation et de concurrence d'états...")
        bugs = []
        snap = context.get("snapshot")
        if snap and hasattr(snap, "activeCoroutineCount") and snap.activeCoroutineCount > 50:
            bugs.append({
                "specialist": self.name,
                "domain": self.domain,
                "severity": "MEDIUM",
                "title": f"Accumulation de Coroutines Zombies ({snap.activeCoroutineCount} actives)",
                "description": "Des coroutines d'animation sont instanciées à chaque transition sans arrêt préalable.",
                "reproduction": ["Changer d'état d'animation rapidement (Run <-> Idle)"],
                "fix": "if (_animCoroutine != null) StopCoroutine(_animCoroutine);\n_animCoroutine = StartCoroutine(PlayAnim(clip));"
            })
        return bugs