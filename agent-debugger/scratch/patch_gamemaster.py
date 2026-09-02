import os

# 1. Update DebuggerServer.cs
def patch_server(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    gm_rpc = """                // === GAME MASTER / GOD MODE POWERS ===
                if (method == "gamemaster.setGodMode")
                {
                    bool enabled = true;
                    if (request.args != null && request.args.Length > 0) bool.TryParse(request.args[0], out enabled);
                    AIGameMasterController.Instance?.SetGodMode(enabled);
                    client.SendResponse(request.id, new { success = true, godMode = enabled });
                    return;
                }
                if (method == "gamemaster.setFlyMode")
                {
                    bool enabled = true;
                    float vSpeed = 0f;
                    if (request.args != null && request.args.Length > 0) bool.TryParse(request.args[0], out enabled);
                    if (request.args != null && request.args.Length > 1) float.TryParse(request.args[1], out vSpeed);
                    AIGameMasterController.Instance?.SetFlyMode(enabled, vSpeed);
                    client.SendResponse(request.id, new { success = true, flyMode = enabled });
                    return;
                }
                if (method == "gamemaster.teleport")
                {
                    float x = 0f, y = 0f, z = 0f;
                    if (request.args != null && request.args.Length > 0) float.TryParse(request.args[0], out x);
                    if (request.args != null && request.args.Length > 1) float.TryParse(request.args[1], out y);
                    if (request.args != null && request.args.Length > 2) float.TryParse(request.args[2], out z);
                    AIGameMasterController.Instance?.TeleportPlayer(x, y, z);
                    client.SendResponse(request.id, new { success = true, x, y, z });
                    return;
                }
                if (method == "gamemaster.resetLevel")
                {
                    AIGameMasterController.Instance?.ResetLevel();
                    client.SendResponse(request.id, new { success = true });
                    return;
                }
"""
    if "gamemaster.setGodMode" not in code and 'if (method == "player.explore")' in code:
        code = code.replace('if (method == "player.explore")', gm_rpc + '\n                if (method == "player.explore")')
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched DebuggerServer with GameMaster in {path}")

patch_server(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")

# 2. Update AIDebuggerMenu.cs
def patch_menu(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    if "AIGameMasterController" not in code:
        code = code.replace("go.AddComponent<AIPlayerDriver>();", "go.AddComponent<AIPlayerDriver>();\n        go.AddComponent<AIGameMasterController>();")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched AIDebuggerMenu in {path}")

patch_menu(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")
patch_menu(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")

# 3. Update unity_client.py
cl_path = r"agent-debugger\debugger_client\unity_client.py"
with open(cl_path, "r", encoding="utf-8") as f:
    cl_code = f.read()

gm_helpers = """    async def set_god_mode(self, enabled: bool = True) -> bool:
        res = await self.call("gamemaster.setGodMode", {"args": [str(enabled).lower()]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def set_fly_mode(self, enabled: bool = True, vertical_speed: float = 0.0) -> bool:
        res = await self.call("gamemaster.setFlyMode", {"args": [str(enabled).lower(), str(vertical_speed)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def teleport(self, x: float, y: float, z: float = 0.0) -> bool:
        res = await self.call("gamemaster.teleport", {"args": [str(x), str(y), str(z)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def reset_level(self) -> bool:
        res = await self.call("gamemaster.resetLevel")
        return res.get("success", False) if isinstance(res, dict) else False

"""
if "set_god_mode" not in cl_code and "async def start_player_exploration" in cl_code:
    cl_code = cl_code.replace("    async def start_player_exploration", gm_helpers + "    async def start_player_exploration")
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write(cl_code)
    print("Patched unity_client.py with GameMaster helpers.")

# 4. Update main.py
main_path = r"agent-debugger\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    main_code = f.read()

if "--godmode" not in main_code:
    main_code = main_code.replace(
        'parser.add_argument("--hunt"',
        'parser.add_argument("--godmode", action="store_true", help="Activer le GodMode (Invulnérabilité totale)")\n    parser.add_argument("--fly", action="store_true", help="Activer le vol libre (Fly/NoClip)")\n    parser.add_argument("--reset", action="store_true", help="Réinitialiser / Recharger le niveau instantanément")\n    parser.add_argument("--teleport", nargs=3, type=float, metavar=("X", "Y", "Z"), help="Téléporter le joueur aux coordonnées X Y Z")\n    parser.add_argument("--hunt"'
    )

    gm_cli_exec = """        if args.godmode:
            print("[GAME MASTER] Activation du GodMode...")
            await client.set_god_mode(True)
            print("[OK] Joueur invulnérable.")
            return

        if args.fly:
            print("[GAME MASTER] Activation du Vol Libre (Fly / NoClip)...")
            await client.set_fly_mode(True, 3.0)
            print("[OK] Vol actif.")
            return

        if args.reset:
            print("[GAME MASTER] Rechargement du niveau...")
            await client.reset_level()
            print("[OK] Niveau réinitialisé.")
            return

        if args.teleport:
            x, y, z = args.teleport
            print(f"[GAME MASTER] Téléportation vers ({x}, {y}, {z})...")
            await client.teleport(x, y, z)
            print("[OK] Téléporté.")
            return
"""
    if "if args.godmode:" not in main_code and "if args.hunt:" in main_code:
        main_code = main_code.replace("if args.hunt:", gm_cli_exec + "\n        if args.hunt:")

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_code)
    print("Patched main.py with GameMaster CLI options.")