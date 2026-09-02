import asyncio
from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class PhysicsSpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : Physique, Collisions 2D/3D, Gravité & Tunneling.
    Pilote activement le joueur dans l'espace 3D pour tester les collisions et franchissements de murs.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Physique", "Physics & Collisions", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"   [{self.name}] Pilotage physique du joueur : Sprint & Fuzzing contre les murs...")
        bugs = []

        # 1. Action active : Faire sprinter et fuzzer le personnage
        try:
            if hasattr(self.client, "drive_player_fuzz"):
                await self.client.drive_player_fuzz(duration=1.5)
            elif hasattr(self.client, "drive_player_move"):
                await self.client.drive_player_move(move_x=0.0, move_z=1.0, yaw=0.5, sprint=True, jump=True, duration=1.5)
        except Exception:
            pass

        # 2. Vérification des coordonnées et franchissements de seuils
        if hasattr(self.client, "get_spatial_3d"):
            try:
                entities = await self.client.get_spatial_3d()
                for e in (entities or []):
                    pos_y = e.get("posY", 0.0) if isinstance(e, dict) else getattr(e, "posY", 0.0)
                    name = e.get("name", "Unknown") if isinstance(e, dict) else getattr(e, "name", "Unknown")
                    if pos_y < -20.0:
                        bugs.append({
                            "specialist": self.name,
                            "domain": self.domain,
                            "severity": "CRITICAL",
                            "title": f"Tunneling physique & Chute hors du monde sur '{name}'",
                            "description": f"L'objet a traversé les colliders lors de la course et se trouve à Y={pos_y:.1f}.",
                            "reproduction": ["Sprinter vers un mur", "Sauter simultanément sous haute vélocité"],
                            "fix": "GetComponent<Rigidbody>().collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;"
                        })
            except Exception:
                pass

        return bugs