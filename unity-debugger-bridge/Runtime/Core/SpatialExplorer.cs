using System;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Core
{
    [AddComponentMenu("AI Debugger/Spatial Explorer")]
    public class SpatialExplorer : MonoBehaviour
    {
        private static SpatialExplorer _instance;
        public static SpatialExplorer Instance => _instance;

        public int ScannedSectorsCount { get; private set; }
        public int UnreachableGeometryHolesCount { get; private set; }

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

        public object ScanLevelGeometry(Vector3 center, float radius = 25f, int rayCount = 36)
        {
            ScannedSectorsCount++;
            var hits = new List<object>();
            int missingColliders = 0;

            for (int i = 0; i < rayCount; i++)
            {
                float angle = i * (360f / rayCount) * Mathf.Deg2Rad;
                Vector3 dir = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                if (Physics.Raycast(center + Vector3.up * 1.0f, dir, out RaycastHit hit, radius))
                {
                    hits.Add(new
                    {
                        hitObject = hit.collider.gameObject.name,
                        distance = hit.distance,
                        normal = hit.normal,
                        isStatic = hit.collider.gameObject.isStatic
                    });
                }
                else
                {
                    missingColliders++;
                }
            }

            if (missingColliders > (rayCount / 2))
            {
                UnreachableGeometryHolesCount++;
            }

            return new
            {
                center = center,
                radius = radius,
                scannedRays = rayCount,
                detectedWalls = hits.Count,
                openBounds = missingColliders
            };
        }
    }
}