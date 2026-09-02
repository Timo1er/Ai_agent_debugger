import os

def patch_server(server_path):
    if not os.path.exists(server_path):
        return
    with open(server_path, "r", encoding="utf-8") as f:
        code = f.read()

    old_send = """        public void SendResponse(string id, object result)
        {
            string json = JsonUtility.ToJson(new RpcResponse { id = id, result = result });
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }"""

    new_send = """        public void SendResponse(string id, object result)
        {
            string resultJson = "{}";
            if (result != null)
            {
                if (result is string str)
                    resultJson = "\\\"" + str.Replace("\\\"", "\\\\\\\"") + "\\\"";
                else if (result.GetType().IsPrimitive || result is bool)
                    resultJson = result.ToString().ToLower();
                else
                    resultJson = JsonUtility.ToJson(result);
            }
            if (string.IsNullOrEmpty(resultJson)) resultJson = "{}";
            string json = "{\\\"jsonrpc\\\":\\\"2.0\\\",\\\"id\\\":\\\"" + id + "\\\",\\\"result\\\":" + resultJson + "}";
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }"""

    old_err = """        public void SendError(string id, int code, string message)
        {
            string json = JsonUtility.ToJson(new RpcResponse
            {
                id = id,
                error = new RpcError { code = code, message = message }
            });
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }"""

    new_err = """        public void SendError(string id, int code, string message)
        {
            string safeMsg = (message ?? "").Replace("\\\"", "\\\\\\\"");
            string idPart = id != null ? ("\\\"id\\\":\\\"" + id + "\\\",") : "";
            string json = "{\\\"jsonrpc\\\":\\\"2.0\\\"," + idPart + "\\\"error\\\":{\\\"code\\\":" + code + ",\\\"message\\\":\\\"" + safeMsg + "\\\"}}";
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }"""

    if old_send in code:
        code = code.replace(old_send, new_send)
    if old_err in code:
        code = code.replace(old_err, new_err)

    with open(server_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Patched {server_path}")

patch_server(r"C:\Users\timot\My project (1)\Assets\AIDebuggerBridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"c:\Users\timot\Documents\Git dev\AI-agent-debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")