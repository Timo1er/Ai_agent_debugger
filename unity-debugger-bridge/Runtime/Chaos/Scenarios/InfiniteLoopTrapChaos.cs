using System;
using System.Diagnostics;
using UnityEngine;
using AIDebugger.Chaos;

namespace AIDebugger.Chaos.Scenarios
{
    public class InfiniteLoopTrapChaos : ChaosScenarioBase
    {
        public override string ScenarioName => "infinite_loop_trap";
        public override string Description => "Simulates a heavy blocking loop / hang during Update that severely degrades frame rate down to < 5 FPS, triggering watchdog alarms.";

        [SerializeField] private int _iterationsPerFrame = 5000000;

        public override bool Inject(string parametersJson)
        {
            IsActive = true;
            return true;
        }

        private void Update()
        {
            if (!IsActive) return;

            // Artificial heavy workload simulating blocking while(true) or pathfinding hang
            double dummy = 0;
            for (int i = 0; i < _iterationsPerFrame; i++)
            {
                dummy += Math.Sin(i) * Math.Cos(i);
            }
        }

        public override void Revert()
        {
            IsActive = false;
        }

        public override object GetStatus()
        {
            return new
            {
                iterationsPerFrame = _iterationsPerFrame,
                isLagging = IsActive
            };
        }
    }
}