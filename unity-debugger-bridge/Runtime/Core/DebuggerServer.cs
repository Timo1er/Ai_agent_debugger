#pragma warning disable CS4014, CS0618
#pragma warning disable CS0619
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using AIDebugger.Telemetry;
using AIDebugger.Chaos;

namespace AIDebugger.Core
{
    [AddComponentMenu("AI Debugger/Debugger Server")]
    [DefaultExecutionOrder(-9999)]
    public class DebuggerServer : MonoBehaviour
    {
        private static DebuggerServer _instance;
        public static DebuggerServer Instance => _instance;

        [Header("Network Configuration")]
        [SerializeField] private int _port = 8080;
        [SerializeField] private bool _autoStartOnAwake = true;

        private TcpListener _tcpListener;
        private CancellationTokenSource _cts;
        private readonly List<WebSocketClientConnection> _activeClients = new List<WebSocketClientConnection>();
        private readonly object _clientsLock = new object();

        public bool IsRunning { get; private set; }

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);

            if (_autoStartOnAwake)
            {
                StartServer();
            }
        }

        private void OnDestroy()
        {
            StopServer();
        }

        public void StartServer(int port = -1)
        {
            if (IsRunning) return;
            if (port > 0) _port = port;

            _cts = new CancellationTokenSource();
            try
            {
                _tcpListener = new TcpListener(IPAddress.Any, _port);
                _tcpListener.Start();
                IsRunning = true;
                Debug.Log($"[AIDebugger] Server listening on ws://127.0.0.1:{_port}");
                Task.Run(() => AcceptClientsAsync(_cts.Token));
            }
            catch (Exception ex)
            {
                Debug.LogError($"[AIDebugger] Failed to start server on port {_port}: {ex.Message}");
            }
        }

        public void StopServer()
        {
            if (!IsRunning) return;
            IsRunning = false;

            _cts?.Cancel();
            try
            {
                _tcpListener?.Stop();
            }
            catch { }

            lock (_clientsLock)
            {
                foreach (var client in _activeClients)
                {
                    client.Close();
                }
                _activeClients.Clear();
            }

            Debug.Log("[AIDebugger] Server stopped.");
        }

        private async Task AcceptClientsAsync(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && IsRunning)
            {
                try
                {
                    var tcpClient = await _tcpListener.AcceptTcpClientAsync();
                    var clientConn = new WebSocketClientConnection(tcpClient, this);
                    Task.Run(() => clientConn.HandleAsync(ct));
                }
                catch (ObjectDisposedException) { break; }
                catch (Exception ex)
                {
                    if (IsRunning) Debug.LogWarning($"[AIDebugger] Accept client error: {ex.Message}");
                }
            }
        }

        internal void RegisterClient(WebSocketClientConnection client)
        {
            lock (_clientsLock)
            {
                _activeClients.Add(client);
            }
        }

        internal void UnregisterClient(WebSocketClientConnection client)
        {
            lock (_clientsLock)
            {
                _activeClients.Remove(client);
            }
        }

        public void BroadcastNotification(string method, object payload)
        {
            BroadcastEvent(method, payload);
        }

        public void BroadcastEvent(string eventName, object payload)
        {
            var evt = new RpcEvent { @event = eventName, payload = payload };
            string json = JsonUtility.ToJson(evt);
            BroadcastText(json);
        }

        public void BroadcastText(string message)
        {
            byte[] frame = WebSocketFrameHelper.EncodeTextFrame(message);
            lock (_clientsLock)
            {
                foreach (var client in _activeClients)
                {
                    client.SendRaw(frame);
                }
            }
        }

        public void HandleRpcMessage(WebSocketClientConnection client, string jsonMessage)
        {
            RpcRequest request = null;
            try
            {
                request = JsonUtility.FromJson<RpcRequest>(jsonMessage);
            }
            catch (Exception ex)
            {
                client.SendError(null, -32700, "Parse error: " + ex.Message);
                return;
            }

            if (request == null || string.IsNullOrEmpty(request.method))
            {
                client.SendError(null, -32600, "Invalid Request");
                return;
            }

            MainThreadDispatcher.Enqueue(() =>
            {
                ProcessMethodCall(client, request);
            });
        }

        private void ProcessMethodCall(WebSocketClientConnection client, RpcRequest request)
        {
            try
            {
                string method = request.method;

                                // === HUD VISUAL OVERLAY ===
                if (method == "hud.update")
                {
                    string agent = (request.args != null && request.args.Length > 0) ? request.args[0] : "Superviseur IA";
                    string act = (request.args != null && request.args.Length > 1) ? request.args[1] : "";
                    string det = (request.args != null && request.args.Length > 2) ? request.args[2] : "";
                    bool isAlrt = (request.args != null && request.args.Length > 3) && bool.TryParse(request.args[3], out var b) && b;
                    AIDebuggerOverlay.Instance?.SetStatus(agent, act, det, isAlrt);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                // === TELEMETRY ===
                if (method == "telemetry.getSnapshot" || method == "get_telemetry_snapshot")
                {
                    var streamer = TelemetryStreamer.Instance;
                    var snap = streamer != null ? streamer.CreateSnapshot() : new TelemetrySnapshot
                    {
                        timestamp = DateTime.UtcNow.ToString("o"),
                        frameCount = Time.frameCount,
                        timeSinceStartup = Time.realtimeSinceStartup,
                        timeScale = Time.timeScale,
                        metrics = ProfilerMetricsCollector.Instance != null ? ProfilerMetricsCollector.Instance.GetCurrentMetrics() : null,
                        recentLogs = LogInterceptor.Instance != null ? LogInterceptor.Instance.GetRecentLogs(20) : new List<LogEntryDto>()
                    };
                    client.SendResponse(request.id, snap);
                    return;
                }

                // === INSPECTOR ===
                if (method == "inspector.getHierarchy" || method == "get_hierarchy")
                {
                    var tree = RuntimeInspector.GetHierarchyTree();
                    client.SendResponse(request.id, tree);
                    return;
                }

                if (method == "inspector.findObjects")
                {
                    var list = RuntimeInspector.FindGameObjects();
                    client.SendResponse(request.id, list);
                    return;
                }

                if (method == "inspector.setMember" || method == "set_property")
                {
                    if (request.args != null && request.args.Length >= 4)
                    {
                        int targetId = int.Parse(request.args[0]);
                        string compName = request.args[1];
                        string memberName = request.args[2];
                        string valStr = request.args[3];
                        bool ok = RuntimeInspector.SetPropertyValue(targetId, compName, memberName, valStr);
                        client.SendResponse(request.id, new { success = ok });
                    }
                    else
                    {
                        client.SendResponse(request.id, new { success = true });
                    }
                    return;
                }

                if (method == "inspector.invokeMethod" || method == "invoke_method")
                {
                    if (request.args != null && request.args.Length >= 3)
                    {
                        int targetId = int.Parse(request.args[0]);
                        string compName = request.args[1];
                        string methodName = request.args[2];
                        var methodArgs = new string[request.args.Length - 3];
                        Array.Copy(request.args, 3, methodArgs, 0, methodArgs.Length);
                        object ret = RuntimeInspector.InvokeMethod(targetId, compName, methodName, methodArgs);
                        client.SendResponse(request.id, new { success = true, returnValue = ret });
                    }
                    else
                    {
                        client.SendResponse(request.id, new { success = true });
                    }
                    return;
                }

                if (method == "inspector.setComponentActive")
                {
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                if (method == "inspector.setGameObjectActive")
                {
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                                // === PLAYER ACTIVE DRIVER ===
                if (method == "player.move")
                {
                    float mx = 0f, mz = 1f, yaw = 0f, dur = 2f;
                    bool sprint = false, jump = false;
                    if (request.args != null)
                    {
                        if (request.args.Length > 0) float.TryParse(request.args[0], out mx);
                        if (request.args.Length > 1) float.TryParse(request.args[1], out mz);
                        if (request.args.Length > 2) float.TryParse(request.args[2], out yaw);
                        if (request.args.Length > 3) bool.TryParse(request.args[3], out sprint);
                        if (request.args.Length > 4) bool.TryParse(request.args[4], out jump);
                        if (request.args.Length > 5) float.TryParse(request.args[5], out dur);
                    }
                    AIPlayerDriver.Instance?.DriveMove(mx, mz, yaw, sprint, jump, dur);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                if (method == "player.fuzz")
                {
                    float dur = 3f;
                    if (request.args != null && request.args.Length > 0) float.TryParse(request.args[0], out dur);
                    AIPlayerDriver.Instance?.FuzzWallImpact(dur);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                                // === DEEP QA LAB ROUTING ===
                if (method == "spatial.scanGeometry")
                {
                    Vector3 center = Vector3.zero;
                    var p = GameObject.FindGameObjectWithTag("Player");
                    if (p != null) center = p.transform.position;
                    var res = SpatialExplorer.Instance != null ? SpatialExplorer.Instance.ScanLevelGeometry(center) : new { };
                    client.SendResponse(request.id, res);
                    return;
                }

                if (method == "physics.stressCorner")
                {
                    var p = GameObject.FindGameObjectWithTag("Player");
                    PhysicalStressLab.Instance?.ExecuteCornerWedgeStress(p, 2.0f);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                if (method == "physics.stressVelocity")
                {
                    var p = GameObject.FindGameObjectWithTag("Player");
                    PhysicalStressLab.Instance?.ExecuteVelocityInversionStress(p, 1.5f);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                if (method == "combat.fuzzWeapons")
                {
                    var p = GameObject.FindGameObjectWithTag("Player");
                    CombatActionFuzzer.Instance?.FuzzWeaponStateCycle(p, 2.0f);
                    client.SendResponse(request.id, new { success = true });
                    return;
                }

                if (method == "oracle.microAudit")
                {
                    var res = MicroscopicInvariantOracle.Instance != null ? MicroscopicInvariantOracle.Instance.RunMicroscopicAudit() : new { };
                    client.SendResponse(request.id, res);
                    return;
                }

                // === TIMESTEP ===
                if (method == "timestep.pause" || method == "pause_game")
                {
                    TimeStepController.Instance?.Pause();
                    client.SendResponse(request.id, new { isPaused = true });
                    return;
                }

                if (method == "timestep.resume" || method == "resume_game")
                {
                    TimeStepController.Instance?.Resume();
                    client.SendResponse(request.id, new { isPaused = false });
                    return;
                }

                if (method == "timestep.stepFrames" || method == "step_frame")
                {
                    int frames = 1;
                    if (request.args != null && request.args.Length > 0)
                        int.TryParse(request.args[0], out frames);
                    TimeStepController.Instance?.StepFrames(frames);
                    client.SendResponse(request.id, new { steppedFrames = frames });
                    return;
                }

                if (method == "timestep.setTimeScale")
                {
                    float sc = 1.0f;
                    if (request.args != null && request.args.Length > 0) float.TryParse(request.args[0], out sc);
                    TimeStepController.Instance?.SetTimeScale(sc);
                    client.SendResponse(request.id, new { scale = sc });
                    return;
                }

                // === DYNAMIC C# EVAL ===
                if (method == "eval.executeCode" || method == "eval_csharp")
                {
                    string code = (request.args != null && request.args.Length > 0) ? request.args[0] : "";
                    var res = DynamicCodeEvaluator.Execute(code);
                    client.SendResponse(request.id, res);
                    return;
                }

                // === SPATIAL TRACKER ===
                if (method == "spatial.getEntities3D")
                {
                    var ents = SpatialTracker.Instance != null ? SpatialTracker.Instance.GetSnapshot3D() : new List<SpatialEntity3D>();
                    client.SendResponse(request.id, ents);
                    return;
                }

                if (method == "spatial.getEntities2D")
                {
                    var ents = SpatialTracker.Instance != null ? SpatialTracker.Instance.GetSnapshot2D() : new List<SpatialEntity2D>();
                    client.SendResponse(request.id, ents);
                    return;
                }

                if (method == "spatial.raycast3D")
                {
                    client.SendResponse(request.id, new { hit = false });
                    return;
                }

                // === CHAOS ENGINE ===
                if (method == "chaos.inject" || method == "trigger_chaos")
                {
                    string sc = (request.args != null && request.args.Length > 0) ? request.args[0] : "";
                    bool ok = ChaosEngine.Instance != null && ChaosEngine.Instance.InjectScenario(sc);
                    client.SendResponse(request.id, new { injected = ok, scenario = sc });
                    return;
                }

                if (method == "chaos.reset")
                {
                    ChaosEngine.Instance?.ResetAllScenarios();
                    client.SendResponse(request.id, new { status = "reset_complete" });
                    return;
                }

                if (method == "chaos.getStatus")
                {
                    string activeSc = ChaosEngine.Instance != null ? ChaosEngine.Instance.ActiveScenarioName : null;
                    client.SendResponse(request.id, new { activeScenario = activeSc });
                    return;
                }

                if (method == "ping")
                {
                    client.SendResponse(request.id, new { pong = true, time = Time.time });
                    return;
                }

                client.SendError(request.id, -32601, $"Method '{request.method}' not found");
            }
            catch (Exception ex)
            {
                client.SendError(request.id, -32000, "Internal error: " + ex.Message);
            }
        }
    }

    public class WebSocketClientConnection
    {
        private readonly TcpClient _tcpClient;
        private readonly DebuggerServer _server;
        private readonly NetworkStream _stream;
        private readonly object _sendLock = new object();

        public WebSocketClientConnection(TcpClient tcpClient, DebuggerServer server)
        {
            _tcpClient = tcpClient;
            _server = server;
            _stream = tcpClient.GetStream();
        }

        public async Task HandleAsync(CancellationToken ct)
        {
            _server.RegisterClient(this);
            try
            {
                bool handshaked = await DoHandshakeAsync(ct);
                if (!handshaked) return;

                byte[] buffer = new byte[8192];
                var messageBuffer = new List<byte>();

                while (!ct.IsCancellationRequested && _tcpClient.Connected)
                {
                    int bytesRead = await _stream.ReadAsync(buffer, 0, buffer.Length, ct);
                    if (bytesRead <= 0) break;

                    int offset = 0;
                    while (offset < bytesRead)
                    {
                        var (payload, bytesConsumed, isClose) = WebSocketFrameHelper.DecodeFrame(buffer, offset, bytesRead - offset);
                        if (isClose) return;

                        if (bytesConsumed == 0) break;
                        offset += bytesConsumed;

                        if (payload != null)
                        {
                            messageBuffer.AddRange(payload);
                            string text = Encoding.UTF8.GetString(messageBuffer.ToArray());
                            messageBuffer.Clear();
                            _server.HandleRpcMessage(this, text);
                        }
                    }
                }
            }
            catch { }
            finally
            {
                Close();
                _server.UnregisterClient(this);
            }
        }

        private async Task<bool> DoHandshakeAsync(CancellationToken ct)
        {
            byte[] headerBuf = new byte[2048];
            int read = await _stream.ReadAsync(headerBuf, 0, headerBuf.Length, ct);
            if (read <= 0) return false;

            string requestStr = Encoding.UTF8.GetString(headerBuf, 0, read);
            var match = Regex.Match(requestStr, @"Sec-WebSocket-Key:\s*(.+)\r\n", RegexOptions.IgnoreCase);
            if (!match.Success) return false;

            string secKey = match.Groups[1].Value.Trim();
            string magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
            string acceptKey;
            using (var sha1 = SHA1.Create())
            {
                byte[] hash = sha1.ComputeHash(Encoding.UTF8.GetBytes(secKey + magic));
                acceptKey = Convert.ToBase64String(hash);
            }

            string responseStr = "HTTP/1.1 101 Switching Protocols\r\n" +
                                 "Upgrade: websocket\r\n" +
                                 "Connection: Upgrade\r\n" +
                                 "Sec-WebSocket-Accept: " + acceptKey + "\r\n\r\n";

            byte[] responseBytes = Encoding.UTF8.GetBytes(responseStr);
            await _stream.WriteAsync(responseBytes, 0, responseBytes.Length, ct);
            return true;
        }

        public void SendResponse(string id, object result)
        {
            string resultJson = "{}";
            if (result != null)
            {
                if (result is string str)
                    resultJson = "\"" + str.Replace("\"", "\\\"") + "\"";
                else if (result.GetType().IsPrimitive || result is bool)
                    resultJson = result.ToString().ToLower();
                else
                    resultJson = JsonUtility.ToJson(result);
            }
            if (string.IsNullOrEmpty(resultJson)) resultJson = "{}";
            string json = "{\"jsonrpc\":\"2.0\",\"id\":\"" + id + "\",\"result\":" + resultJson + "}";
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }

        public void SendError(string id, int code, string message)
        {
            string safeMsg = (message ?? "").Replace("\"", "\\\"");
            string idPart = id != null ? ("\"id\":\"" + id + "\",") : "";
            string json = "{\"jsonrpc\":\"2.0\"," + idPart + "\"error\":{\"code\":" + code + ",\"message\":\"" + safeMsg + "\"}}";
            SendRaw(WebSocketFrameHelper.EncodeTextFrame(json));
        }

        public void SendRaw(byte[] frame)
        {
            lock (_sendLock)
            {
                try
                {
                    if (_tcpClient.Connected)
                    {
                        _stream.Write(frame, 0, frame.Length);
                        _stream.Flush();
                    }
                }
                catch { }
            }
        }

        public void Close()
        {
            try
            {
                _stream?.Close();
                _tcpClient?.Close();
            }
            catch { }
        }
    }

    public static class WebSocketFrameHelper
    {
        public static (byte[] payload, int bytesConsumed, bool isClose) DecodeFrame(byte[] buffer, int offset, int length)
        {
            if (length < 2) return (null, 0, false);

            byte b1 = buffer[offset];
            byte b2 = buffer[offset + 1];

            int opcode = b1 & 0x0F;
            if (opcode == 0x8) return (null, 2, true); // Close frame

            bool masked = (b2 & 0x80) != 0;
            int payloadLen = b2 & 0x7F;
            int cur = offset + 2;

            if (payloadLen == 126)
            {
                if (length < 4) return (null, 0, false);
                payloadLen = (buffer[cur] << 8) | buffer[cur + 1];
                cur += 2;
            }
            else if (payloadLen == 127)
            {
                if (length < 10) return (null, 0, false);
                payloadLen = (int)((ulong)buffer[cur] << 56 | (ulong)buffer[cur + 1] << 48 | (ulong)buffer[cur + 2] << 40 | (ulong)buffer[cur + 3] << 32 |
                                   (ulong)buffer[cur + 4] << 24 | (ulong)buffer[cur + 5] << 16 | (ulong)buffer[cur + 6] << 8 | (ulong)buffer[cur + 7]);
                cur += 8;
            }

            byte[] masks = null;
            if (masked)
            {
                if (offset + length < cur + 4) return (null, 0, false);
                masks = new byte[] { buffer[cur], buffer[cur + 1], buffer[cur + 2], buffer[cur + 3] };
                cur += 4;
            }

            if (offset + length < cur + payloadLen) return (null, 0, false);

            byte[] payload = new byte[payloadLen];
            Array.Copy(buffer, cur, payload, 0, payloadLen);

            if (masked && masks != null)
            {
                for (int i = 0; i < payloadLen; i++)
                {
                    payload[i] = (byte)(payload[i] ^ masks[i % 4]);
                }
            }

            int totalConsumed = (cur + payloadLen) - offset;
            return (payload, totalConsumed, false);
        }

        public static byte[] EncodeTextFrame(string message)
        {
            byte[] msgBytes = Encoding.UTF8.GetBytes(message);
            var frame = new List<byte>();

            frame.Add(0x81); // FIN + Text opcode (0x1)

            if (msgBytes.Length <= 125)
            {
                frame.Add((byte)msgBytes.Length);
            }
            else if (msgBytes.Length <= 65535)
            {
                frame.Add(126);
                frame.Add((byte)((msgBytes.Length >> 8) & 0xFF));
                frame.Add((byte)(msgBytes.Length & 0xFF));
            }
            else
            {
                frame.Add(127);
                for (int i = 7; i >= 0; i--)
                {
                    frame.Add((byte)((msgBytes.Length >> (8 * i)) & 0xFF));
                }
            }

            frame.AddRange(msgBytes);
            return frame.ToArray();
        }
    }
}