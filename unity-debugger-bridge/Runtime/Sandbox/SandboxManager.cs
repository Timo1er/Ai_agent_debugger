using System;
using UnityEngine;
using AIDebugger.Core;
using AIDebugger.Telemetry;
using AIDebugger.Chaos;

namespace AIDebugger.Sandbox
{
    public class SandboxManager : MonoBehaviour
    {
        private static SandboxManager _instance;
        public static SandboxManager Instance => _instance;

        public Player2DController player2D;
        public Player3DController player3D;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;

            // Initialize all core subsystems
            _ = MainThreadDispatcher.Instance;
            _ = TimeStepController.Instance;
            _ = DebuggerServer.Instance;
            _ = TelemetryStreamer.Instance;
            _ = ChaosEngine.Instance;
        }

        private void Start()
        {
            Debug.Log("[AIDebugger] SandboxManager initialized with 2D & 3D environments.");
        }
    }
}