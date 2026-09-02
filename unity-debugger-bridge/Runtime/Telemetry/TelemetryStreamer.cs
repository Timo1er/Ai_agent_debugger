using System;
using UnityEngine;
using AIDebugger.Core;

namespace AIDebugger.Telemetry
{
    [DefaultExecutionOrder(-9998)]
    public class TelemetryStreamer : MonoBehaviour
    {
        private static TelemetryStreamer _instance;
        public static TelemetryStreamer Instance => _instance;

        [Header("Stream Settings")]
        [SerializeField] private float _streamIntervalSeconds = 0.2f; // 5 Hz
        [SerializeField] private bool _autoStream = true;

        private float _lastStreamTime = 0f;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);

            // Ensure sub-collectors exist
            if (GetComponent<LogInterceptor>() == null) gameObject.AddComponent<LogInterceptor>();
            if (GetComponent<SpatialTracker>() == null) gameObject.AddComponent<SpatialTracker>();
            if (GetComponent<ProfilerMetricsCollector>() == null) gameObject.AddComponent<ProfilerMetricsCollector>();
        }

        private void Update()
        {
            if (!_autoStream) return;
            if (Time.unscaledTime - _lastStreamTime >= _streamIntervalSeconds)
            {
                _lastStreamTime = Time.unscaledTime;
                BroadcastSnapshot();
            }
        }

        public TelemetrySnapshot CreateSnapshot()
        {
            var snapshot = new TelemetrySnapshot
            {
                timestamp = DateTime.UtcNow.ToString("o"),
                frameCount = Time.frameCount,
                timeSinceStartup = Time.realtimeSinceStartup,
                timeScale = Time.timeScale,
                metrics = ProfilerMetricsCollector.Instance != null ? ProfilerMetricsCollector.Instance.GetCurrentMetrics() : null,
                recentLogs = LogInterceptor.Instance != null ? LogInterceptor.Instance.GetRecentLogs(20) : null,
                entities2D = SpatialTracker.Instance != null ? SpatialTracker.Instance.GetSnapshot2D() : null,
                entities3D = SpatialTracker.Instance != null ? SpatialTracker.Instance.GetSnapshot3D() : null,
                recentCollisions = SpatialTracker.Instance != null ? SpatialTracker.Instance.GetRecentCollisions(10) : null,
                activeChaosScenario = AIDebugger.Chaos.ChaosEngine.Instance != null ? AIDebugger.Chaos.ChaosEngine.Instance.ActiveScenarioName : null
            };
            return snapshot;
        }

        public void BroadcastSnapshot()
        {
            if (DebuggerServer.Instance != null && DebuggerServer.Instance.IsRunning)
            {
                var snap = CreateSnapshot();
                DebuggerServer.Instance.BroadcastNotification("telemetry.snapshot", snap);
            }
        }
    }
}