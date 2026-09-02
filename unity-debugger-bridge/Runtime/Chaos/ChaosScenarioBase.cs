using System;
using UnityEngine;

namespace AIDebugger.Chaos
{
    public abstract class ChaosScenarioBase : MonoBehaviour
    {
        public abstract string ScenarioName { get; }
        public abstract string Description { get; }
        public bool IsActive { get; protected set; }

        public abstract bool Inject(string parametersJson);
        public abstract void Revert();
        public abstract object GetStatus();
    }
}