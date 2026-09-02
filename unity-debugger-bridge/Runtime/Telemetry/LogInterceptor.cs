using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using UnityEngine;
using AIDebugger.Core;

namespace AIDebugger.Telemetry
{
    public class LogInterceptor : MonoBehaviour
    {
        private static LogInterceptor _instance;
        public static LogInterceptor Instance => _instance;

        private const int MaxLogHistory = 500;
        private readonly ConcurrentQueue<LogEntryDto> _logQueue = new ConcurrentQueue<LogEntryDto>();
        private readonly List<LogEntryDto> _recentLogs = new List<LogEntryDto>();
        private readonly object _listLock = new object();

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);

            Application.logMessageReceivedThreaded += OnLogReceived;
        }

        private void OnDestroy()
        {
            Application.logMessageReceivedThreaded -= OnLogReceived;
        }

        private void Update()
        {
            while (_logQueue.TryDequeue(out var entry))
            {
                lock (_listLock)
                {
                    _recentLogs.Add(entry);
                    if (_recentLogs.Count > MaxLogHistory)
                    {
                        _recentLogs.RemoveAt(0);
                    }
                }

                // If error or exception, stream immediately
                if (entry.type == "Error" || entry.type == "Exception" || entry.type == "Assert")
                {
                    DebuggerServer.Instance?.BroadcastNotification("telemetry.logEvent", entry);
                }
            }
        }

        private void OnLogReceived(string condition, string stackTrace, LogType type)
        {
            var entry = new LogEntryDto
            {
                timestamp = DateTime.UtcNow.ToString("o"),
                frame = Time.frameCount,
                type = type.ToString(),
                message = condition,
                stackTrace = string.IsNullOrEmpty(stackTrace) ? "" : stackTrace
            };

            _logQueue.Enqueue(entry);
        }

        public List<LogEntryDto> GetRecentLogs(int count = 50)
        {
            lock (_listLock)
            {
                int take = Math.Min(count, _recentLogs.Count);
                int start = _recentLogs.Count - take;
                return _recentLogs.GetRange(start, take);
            }
        }

        public void ClearLogs()
        {
            lock (_listLock)
            {
                _recentLogs.Clear();
            }
        }
    }
}