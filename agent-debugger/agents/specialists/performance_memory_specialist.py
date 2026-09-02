from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class PerformanceMemorySpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : Performance Profiler, Fuites Mémoires & Coroutines Zombies.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Performance-Memoire", "Profiler & Memory Leaks", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"   [{self.name}] Analyse du Garbage Collector, FPS et détection de fuites de mémoire...")
        bugs = []
        snap = context.get("snapshot")
        if snap:
            # Memory leak
            mem_mb = 0.0
            if hasattr(snap, "metrics") and snap.metrics and hasattr(snap.metrics, "gcMemoryBytes") and snap.metrics.gcMemoryBytes:
                mem_mb = snap.metrics.gcMemoryBytes / (1024 * 1024)
            elif hasattr(snap, "memoryMB"):
                mem_mb = snap.memoryMB
            
            if mem_mb > 500.0:
                bugs.append({
                    "specialist": self.name,
                    "domain": self.domain,
                    "severity": "HIGH",
                    "title": "Fuite mémoire GC critique (Croissance continue)",
                    "description": f"La mémoire allouée dépasse {mem_mb:.1f} MB sans être recyclée par le GC.",
                    "reproduction": ["Laisser le jeu tourner pendant 60s", "Générer des instances répétées"],
                    "fix": "Purger les listes statiques : staticList.RemoveAll(x => x == null);"
                })

            # FPS drop
            fps = snap.fps if hasattr(snap, "fps") else (snap.metrics.fps if hasattr(snap, "metrics") and snap.metrics else 60.0)
            if fps < 25.0:
                bugs.append({
                    "specialist": self.name,
                    "domain": self.domain,
                    "severity": "HIGH",
                    "title": f"Chute anormale de framerate ({fps:.1f} FPS)",
                    "description": "Opération bloquante sur le thread principal Unity.",
                    "reproduction": ["Entrer dans la scène de jeu"],
                    "fix": "Déplacer l'opération lourde dans Task.Run() ou optimiser Update()."
                })
        return bugs