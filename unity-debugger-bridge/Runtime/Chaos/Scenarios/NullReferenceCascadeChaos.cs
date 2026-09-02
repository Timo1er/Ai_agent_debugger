using System;
using UnityEngine;
using AIDebugger.Chaos;

namespace AIDebugger.Chaos.Scenarios
{
    public class NullReferenceCascadeChaos : ChaosScenarioBase
    {
        public override string ScenarioName => "null_reference_cascade";
        public override string Description => "Corrupts essential component references (e.g. Target transform or weapon reference) causing continuous NullReferenceExceptions during Update loops.";

        private float _logTimer = 0f;

        public override bool Inject(string parametersJson)
        {
            IsActive = true;
            return true;
        }

        private void Update()
        {
            if (!IsActive) return;

            _logTimer += Time.unscaledDeltaTime;
            if (_logTimer >= 0.1f) // 10 NREs per second
            {
                _logTimer = 0f;
                SimulateNullReferenceCrash();
            }
        }

        private void SimulateNullReferenceCrash()
        {
            try
            {
                Transform missingTarget = null;
                Vector3 dest = missingTarget.position; // Triggers NullReferenceException
            }
            catch (Exception ex)
            {
                Debug.LogError("[PlayerController] NullReferenceException in Update() loop: Object reference not set to an instance of an object at PlayerController.UpdateMovement() [targetTransform is NULL]\\n" + ex.StackTrace);
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
                isCrashing = IsActive,
                simulatedTarget = "PlayerController.targetTransform == null"
            };
        }
    }
}