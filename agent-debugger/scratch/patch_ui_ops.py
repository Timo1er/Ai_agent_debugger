import os

# 1. Update DebuggerServer.cs
def patch_server(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    ui_rpc = """                // === UI & GAME MENU OPERATOR ===
                if (method == "ui.getInteractiveElements")
                {
                    var elements = AIGameMenuOperator.Instance != null ? AIGameMenuOperator.Instance.GetInteractiveElements() : new List<UIElementDto>();
                    client.SendResponse(request.id, elements);
                    return;
                }
                if (method == "ui.clickButton")
                {
                    string bName = "";
                    if (request.args != null && request.args.Length > 0) bName = request.args[0];
                    bool ok = AIGameMenuOperator.Instance != null && AIGameMenuOperator.Instance.ClickButtonByName(bName);
                    client.SendResponse(request.id, new { success = ok, button = bName });
                    return;
                }
                if (method == "gamemanager.loadLevel")
                {
                    int lvl = 1;
                    if (request.args != null && request.args.Length > 0) int.TryParse(request.args[0], out lvl);
                    bool ok = AIGameMenuOperator.Instance != null && AIGameMenuOperator.Instance.LoadGameLevel(lvl);
                    client.SendResponse(request.id, new { success = ok, level = lvl });
                    return;
                }
"""
    if "ui.getInteractiveElements" not in code and 'if (method == "gamemaster.setGodMode")' in code:
        code = code.replace('if (method == "gamemaster.setGodMode")', ui_rpc + '\n                if (method == "gamemaster.setGodMode")')
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched DebuggerServer with UI RPC in {path}")

patch_server(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")

# 2. Update AIDebuggerMenu.cs
def patch_menu(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    if "AIGameMenuOperator" not in code:
        code = code.replace("go.AddComponent<AIGameMasterController>();", "go.AddComponent<AIGameMasterController>();\n        go.AddComponent<AIGameMenuOperator>();")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched AIDebuggerMenu in {path}")

patch_menu(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")
patch_menu(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Editor\AIDebuggerMenu.cs")

# 3. Update unity_client.py
cl_path = r"agent-debugger\debugger_client\unity_client.py"
with open(cl_path, "r", encoding="utf-8") as f:
    cl_code = f.read()

ui_helpers = """    async def get_ui_elements(self) -> List[Dict[str, Any]]:
        res = await self.call("ui.getInteractiveElements")
        return res if isinstance(res, list) else []

    async def click_button(self, name: str) -> bool:
        res = await self.call("ui.clickButton", {"args": [name]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def load_game_level(self, level_index: int) -> bool:
        res = await self.call("gamemanager.loadLevel", {"args": [str(level_index)]})
        return res.get("success", False) if isinstance(res, dict) else False

"""
if "get_ui_elements" not in cl_code and "async def set_god_mode" in cl_code:
    cl_code = cl_code.replace("    async def set_god_mode", ui_helpers + "    async def set_god_mode")
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write(cl_code)
    print("Patched unity_client.py with UI helpers.")