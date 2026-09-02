using AIDebugger.Core;
using System;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Core
{
    [AddComponentMenu("AI Debugger/Microscopic Invariant Oracle")]
    public class MicroscopicInvariantOracle : MonoBehaviour
    {
        private static MicroscopicInvariantOracle _instance;
        public static MicroscopicInvariantOracle Instance => _instance;

        private float _lastFrameTime;
        public float MaxFrameHitchMs { get; private set; }
        public int PinkShaderErrorsCount { get; private set; }
        public int NaNCoordinatesCount { get; private set; }

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
            float dtMs = Time.unscaledDeltaTime * 1000f;
            if (dtMs > MaxFrameHitchMs && Time.frameCount > 60)
            {
                MaxFrameHitchMs = dtMs;
            }
        }

        public object RunMicroscopicAudit()
        {
            // 1. Détection de Shaders Roses / Matériaux cassés
            int pinkShaders = 0;
            var renderers = UnityCompat.FindAll<Renderer>(false);
            foreach (var r in renderers)
            {
                if (r.sharedMaterial == null || r.sharedMaterial.shader == null || r.sharedMaterial.shader.name == "Hidden/InternalErrorShader")
                {
                    pinkShaders++;
                }
            }
            PinkShaderErrorsCount = pinkShaders;

            // 2. Détection de coordonnées NaN / Infinity
            int nanCount = 0;
            var transforms = UnityCompat.FindAll<Transform>(false);
            foreach (var t in transforms)
            {
                var p = t.position;
                if (float.IsNaN(p.x) || float.IsNaN(p.y) || float.IsNaN(p.z) ||
                    float.IsInfinity(p.x) || float.IsInfinity(p.y) || float.IsInfinity(p.z))
                {
                    nanCount++;
                }
            }
            NaNCoordinatesCount = nanCount;

            // 3. Audit de la matrice des calques
            bool playerIgnoresEnemies = Physics.GetIgnoreLayerCollision(LayerMask.NameToLayer("Player"), LayerMask.NameToLayer("Enemy"));

            return new
            {
                pinkShadersFound = pinkShaders,
                nanCoordinatesFound = nanCount,
                maxFrameHitchMs = Math.Round(MaxFrameHitchMs, 2),
                playerIgnoresEnemies = playerIgnoresEnemies,
                audioListenerMuted = AudioListener.volume <= 0f,
                activeRenderersCount = renderers.Length
            };
        }
    }
}