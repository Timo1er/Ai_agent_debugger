using System;
using System.Collections.Generic;
using UnityEngine;
using AIDebugger.Chaos;

namespace AIDebugger.Chaos.Scenarios
{
    public class MemoryLeakChaos : ChaosScenarioBase
    {
        public override string ScenarioName => "memory_leak";
        public override string Description => "Continuously allocates unmanaged byte arrays and textures every frame without disposing them, simulating a catastrophic memory leak.";

        private readonly List<Texture2D> _leakedTextures = new List<Texture2D>();
        private readonly List<byte[]> _leakedBuffers = new List<byte[]>();

        public override bool Inject(string parametersJson)
        {
            IsActive = true;
            return true;
        }

        private void Update()
        {
            if (!IsActive) return;

            // Allocate 2 MB buffer per frame
            for (int i = 0; i < 4; i++)
            {
                var buffer = new byte[512 * 1024]; // 512 KB
                for (int j = 0; j < buffer.Length; j += 4096) buffer[j] = 0xAA;
                _leakedBuffers.Add(buffer);
            }

            // Create Texture without destroying
            var tex = new Texture2D(256, 256, TextureFormat.RGBA32, false);
            _leakedTextures.Add(tex);
        }

        public override void Revert()
        {
            IsActive = false;
            foreach (var t in _leakedTextures)
            {
                if (t != null) Destroy(t);
            }
            _leakedTextures.Clear();
            _leakedBuffers.Clear();
            GC.Collect();
        }

        public override object GetStatus()
        {
            return new
            {
                allocatedBuffersCount = _leakedBuffers.Count,
                allocatedTexturesCount = _leakedTextures.Count,
                estimatedLeakedBytes = _leakedBuffers.Count * (512 * 1024)
            };
        }
    }
}