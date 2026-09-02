import os

# 1. Patch DebuggerServer.cs
def patch_server(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    explore_rpc = """                // === PLAYER EXPLORATION ===
                if (method == "player.explore")
                {
                    float dur = 30f;
                    if (request.args != null && request.args.Length > 0) float.TryParse(request.args[0], out dur);
                    AIPlayerDriver.Instance?.StartAutonomousExploration(dur);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }
"""
    if "player.explore" not in code and 'if (method == "player.move")' in code:
        code = code.replace('if (method == "player.move")', explore_rpc + '\n                if (method == "player.move")')
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched DebuggerServer in {path}")

patch_server(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")

# 2. Patch unity_client.py
cl_path = r"agent-debugger\debugger_client\unity_client.py"
with open(cl_path, "r", encoding="utf-8") as f:
    cl_code = f.read()

explore_helper = """    async def start_player_exploration(self, duration: float = 30.0) -> bool:
        res = await self.call("player.explore", {"args": [str(duration)]})
        return res.get("success", False) if isinstance(res, dict) else False

"""
if "start_player_exploration" not in cl_code and "async def drive_player_move" in cl_code:
    cl_code = cl_code.replace("    async def drive_player_move", explore_helper + "    async def drive_player_move")
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write(cl_code)
    print("Patched unity_client.py")

# 3. Patch multi_agent_supervisor.py
sup_path = r"agent-debugger\agents\multi_agent_supervisor.py"
with open(sup_path, "r", encoding="utf-8") as f:
    sup_code = f.read()

old_hud = 'await self._update_unity_hud("Superviseur IA", "Audit Gameplay Approfondi", "Déploiement des règles d\'inspection")'
new_hud = """await self._update_unity_hud("Superviseur IA", "Audit Gameplay Approfondi", "Déploiement des règles d'inspection")
        try:
            if hasattr(self.client, "start_player_exploration"):
                await self.client.start_player_exploration(duration=self.duration_seconds)
        except Exception:
            pass"""

if "start_player_exploration" not in sup_code and old_hud in sup_code:
    sup_code = sup_code.replace(old_hud, new_hud)
    with open(sup_path, "w", encoding="utf-8") as f:
        f.write(sup_code)
    print("Patched multi_agent_supervisor.py")