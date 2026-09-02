import os

# 1. Update DebuggerServer.cs
def patch_server(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    tunnel_rpc = """                // === TUNNELING EVENTS ===
                if (method == "spatial.getTunnelingEvents")
                {
                    var events = TrajectoryTunnelingSentinel.Instance != null ? TrajectoryTunnelingSentinel.Instance.GetRecentEvents() : new List<TunnelingEventDto>();
                    client.SendResponse(request.id, events);
                    return;
                }
"""
    if "spatial.getTunnelingEvents" not in code and 'if (method == "spatial.scanGeometry")' in code:
        code = code.replace('if (method == "spatial.scanGeometry")', tunnel_rpc + '\n                if (method == "spatial.scanGeometry")')
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched DebuggerServer in {path}")

patch_server(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")

# 2. Update AIDebuggerMenu.cs
def patch_menu(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    if "TrajectoryTunnelingSentinel" not in code:
        code = code.replace("go.AddComponent<SpatialTracker>();", "go.AddComponent<SpatialTracker>();\n        go.AddComponent<TrajectoryTunnelingSentinel>();")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched AIDebuggerMenu in {path}")

patch_menu(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")
patch_menu(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")

# 3. Update unity_client.py
cl_path = r"agent-debugger\debugger_client\unity_client.py"
with open(cl_path, "r", encoding="utf-8") as f:
    cl_code = f.read()

tunnel_helper = """    async def get_tunneling_events(self) -> List[Dict[str, Any]]:
        res = await self.call("spatial.getTunnelingEvents")
        return res if isinstance(res, list) else []

"""
if "get_tunneling_events" not in cl_code and "async def scan_geometry_360" in cl_code:
    cl_code = cl_code.replace("    async def scan_geometry_360", tunnel_helper + "    async def scan_geometry_360")
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write(cl_code)
    print("Patched unity_client.py")

# 4. Update physics_specialist.py to report platform tunneling
phys_path = r"agent-debugger\agents\specialists\physics_specialist.py"
phys_code = '''import asyncio
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
                        "fix": "1. Mettre Rigidbody2D.collisionDetectionMode en Continuous.\\n2. Vérifier que la plateforme a un BoxCollider2D ou TilemapCollider2D solide sans isTrigger."
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
'''
with open(phys_path, "w", encoding="utf-8") as f:
    f.write(phys_code)
print("Updated physics_specialist.py")