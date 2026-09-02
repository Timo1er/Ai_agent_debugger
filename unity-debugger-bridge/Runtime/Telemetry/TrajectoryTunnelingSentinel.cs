using System;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Telemetry
{
    [System.Serializable]
    public class TunnelingEventDto
    {
        public string obstacleName;
        public string obstacleType;
        public float fromX, fromY, fromZ;
        public float toX, toY, toZ;
        public float velocityMagnitude;
        public string timestamp;
    }

    /// <summary>
    /// Sentinelle Temps Réel de Trajectoire & Détection de Traversée de Plateformes (Tunneling Sentinel).
    /// Détecte instantanément si le joueur traverse une plateforme solide, un mur ou un sol
    /// sans déclencher la physique normale.
    /// </summary>
    [AddComponentMenu("AI Debugger/Trajectory Tunneling Sentinel")]
    [DefaultExecutionOrder(50)]
    public class TrajectoryTunnelingSentinel : MonoBehaviour
    {
        private static TrajectoryTunnelingSentinel _instance;
        public static TrajectoryTunnelingSentinel Instance => _instance;

        private GameObject _player;
        private Vector3 _lastPos;
        private bool _hasLastPos = false;

        private readonly List<TunnelingEventDto> _tunnelingEvents = new List<TunnelingEventDto>();
        private readonly object _lock = new object();

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

        private void FixedUpdate()
        {
            FindPlayer();
            if (_player == null) return;

            Vector3 currentPos = _player.transform.position;

            if (_hasLastPos)
            {
                CheckTrajectoryCrossings(_lastPos, currentPos);
            }

            _lastPos = currentPos;
            _hasLastPos = true;
        }

        private void FindPlayer()
        {
            if (_player != null && _player.activeInHierarchy) return;
            _player = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (_player != null)
            {
                _lastPos = _player.transform.position;
                _hasLastPos = true;
            }
        }

        private void CheckTrajectoryCrossings(Vector3 from, Vector3 to)
        {
            float dist = Vector3.Distance(from, to);
            if (dist < 0.05f) return;

            // === VÉRIFICATION 2D (PLATEFORMES & SOLS) ===
            var hits2D = Physics2D.LinecastAll(from, to);
            foreach (var hit in hits2D)
            {
                if (hit.collider == null || hit.collider.isTrigger) continue;
                if (hit.collider.gameObject == _player || hit.collider.transform.IsChildOf(_player.transform)) continue;

                // Si le joueur a traversé le collider de la plateforme
                RecordTunneling(hit.collider.gameObject, from, to, "2D Platform / Solid Collider");
            }

            // === VÉRIFICATION 3D ===
            Vector3 dir3D = (to - from).normalized;
            var hits3D = Physics.RaycastAll(from, dir3D, dist);
            foreach (var hit in hits3D)
            {
                if (hit.collider == null || hit.collider.isTrigger) continue;
                if (hit.collider.gameObject == _player || hit.collider.transform.IsChildOf(_player.transform)) continue;

                RecordTunneling(hit.collider.gameObject, from, to, "3D Wall / MeshCollider");
            }
        }

        private void RecordTunneling(GameObject obstacle, Vector3 from, Vector3 to, string type)
        {
            var ev = new TunnelingEventDto
            {
                obstacleName = obstacle.name,
                obstacleType = type,
                fromX = from.x, fromY = from.y, fromZ = from.z,
                toX = to.x, toY = to.y, toZ = to.z,
                velocityMagnitude = Vector3.Distance(from, to) / Time.fixedDeltaTime,
                timestamp = DateTime.UtcNow.ToString("o")
            };

            lock (_lock)
            {
                _tunnelingEvents.Add(ev);
                if (_tunnelingEvents.Count > 50) _tunnelingEvents.RemoveAt(0);
            }

            Debug.LogWarning($"<color=red><b>[AI TUNNELING SENTINEL]</b> Traversée anormale de '{obstacle.name}' détectée ! (De {from} à {to})</color>");
            AIDebuggerOverlay.Instance?.SetStatus("Agent-Physique", $"⚠️ Tunneling sur '{obstacle.name}'", $"Passé au travers ({from.y:F1} -> {to.y:F1})", true);
        }

        public List<TunnelingEventDto> GetRecentEvents()
        {
            lock (_lock)
            {
                return new List<TunnelingEventDto>(_tunnelingEvents);
            }
        }
    }
}