import asyncio
from typing import Dict, Any, List
from .base_specialist import BaseSpecialistAgent

class PhysicsSpecialistAgent(BaseSpecialistAgent):
    """
    Agent Spécialiste : Physique, Collisions 2D/3D, Gravité & Tunneling.
    Détecte en temps réel le tunneling physique et la traversée de plateformes solides.
    """
    def __init__(self, client: Any, llm: Any):
        super().__init__("Agent-Physique", "Physics & Collisions", client, llm)

    async def investigate_and_hunt(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        bugs = []

        # 1. Vérification en temps réel des événements de Tunneling de Plateformes
        if hasattr(self.client, "get_tunneling_events"):
            try:
                events = await self.client.get_tunneling_events()
                for ev in (events or []):
                    obs_name = ev.get("obstacleName", "Plateforme Solide")
                    fy, ty = ev.get("fromY", 0.0), ev.get("toY", 0.0)
                    bugs.append({
                        "specialist": self.name,
                        "domain": self.domain,
                        "severity": "CRITICAL",
                        "title": f"Traversée anormale de plateforme / Tunneling sur '{obs_name}'",
                        "description": f"Le personnage a traversé la plateforme solide '{obs_name}' de Y={fy:.2f} à Y={ty:.2f} sans collision physique.",
                        "fix": "1. Mettre Rigidbody2D.collisionDetectionMode en Continuous.\n2. Vérifier que la plateforme a un BoxCollider2D ou TilemapCollider2D solide sans isTrigger."
                    })
            except Exception:
                pass

        # 2. Vérification des entités 3D et chutes hors limites
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
                            "description": f"L'objet a traversé les colliders et se trouve à Y={pos_y:.1f}.",
                            "fix": "Passer le Rigidbody en CollisionDetectionMode.ContinuousDynamic."
                        })
            except Exception:
                pass

        return bugs
