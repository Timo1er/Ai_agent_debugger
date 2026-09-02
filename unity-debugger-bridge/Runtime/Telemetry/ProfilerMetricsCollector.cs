using System;
using UnityEngine;
using UnityEngine.Profiling;
using AIDebugger.Core;

namespace AIDebugger.Telemetry
{
    public class ProfilerMetricsCollector : MonoBehaviour
    {
        private static ProfilerMetricsCollector _instance;
        public static ProfilerMetricsCollector Instance => _instance;

        private float _fpsAccumulator = 0f;
        private int _fpsFrames = 0;
        private float _currentFps = 60f;
        private float _currentFrameTimeMs = 16.6f;
        private float _fpsTimeLeft = 0.5f;

        public float CurrentFps => _currentFps;
        public float CurrentFrameTimeMs => _currentFrameTimeMs;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Update()
        {
            _fpsTimeLeft -= Time.unscaledDeltaTime;
            _fpsAccumulator += Time.unscaledDeltaTime;
            _fpsFrames++;

            if (_fpsTimeLeft <= 0.0f)
            {
                _currentFps = _fpsFrames / _fpsAccumulator;
                _currentFrameTimeMs = (_fpsAccumulator / _fpsFrames) * 1000f;
                _fpsTimeLeft = 0.5f;
                _fpsAccumulator = 0f;
                _fpsFrames = 0;
            }
        }

        public ProfilerMetrics GetCurrentMetrics()
        {
            var metrics = new ProfilerMetrics
            {
                fps = (float)Math.Round(_currentFps, 1),
                frameTimeMs = (float)Math.Round(_currentFrameTimeMs, 2),
                gcMemoryBytes = GC.GetTotalMemory(false),
                totalAllocatedMemoryBytes = Profiler.GetTotalAllocatedMemoryLong(),
                totalReservedMemoryBytes = Profiler.GetTotalReservedMemoryLong(),
                activeGameObjectsCount = FindObjectsOfType<GameObject>(false).Length,
                totalComponentsCount = FindObjectsOfType<Component>(false).Length,
                drawCallsCount = UnityStatsDrawCalls()
            };
            return metrics;
        }

        private int UnityStatsDrawCalls()
        {
            // Fallback estimation for draw calls in standalone / editor
            return Mathf.Max(1, FindObjectsOfType<Renderer>(false).Length);
        }
    }
}