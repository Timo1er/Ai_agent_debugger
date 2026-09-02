using System;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Chaos
{
    public class ChaosEngine : MonoBehaviour
    {
        private static ChaosEngine _instance;
        public static ChaosEngine Instance => _instance;

        private readonly Dictionary<string, ChaosScenarioBase> _scenarios = new Dictionary<string, ChaosScenarioBase>(StringComparer.OrdinalIgnoreCase);
        private ChaosScenarioBase _currentActiveScenario;

        public string ActiveScenarioName => _currentActiveScenario != null ? _currentActiveScenario.ScenarioName : null;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);

            RegisterBuiltInScenarios();
        }

        private void RegisterBuiltInScenarios()
        {
            RegisterScenario(gameObject.AddComponent<Scenarios.PhysicsTunnelingChaos>());
            RegisterScenario(gameObject.AddComponent<Scenarios.MemoryLeakChaos>());
            RegisterScenario(gameObject.AddComponent<Scenarios.NullReferenceCascadeChaos>());
            RegisterScenario(gameObject.AddComponent<Scenarios.LogicRaceConditionChaos>());
            RegisterScenario(gameObject.AddComponent<Scenarios.InfiniteLoopTrapChaos>());
        }

        public void RegisterScenario(ChaosScenarioBase scenario)
        {
            if (scenario == null) return;
            _scenarios[scenario.ScenarioName] = scenario;
        }

        public bool InjectScenario(string scenarioName, string paramsJson = null)
        {
            ResetAllScenarios();

            if (_scenarios.TryGetValue(scenarioName, out var scenario))
            {
                bool ok = scenario.Inject(paramsJson);
                if (ok)
                {
                    _currentActiveScenario = scenario;
                    Debug.LogWarning("[ChaosEngine] INJECTED scenario: " + scenarioName);
                }
                return ok;
            }

            Debug.LogError("[ChaosEngine] Scenario not found: " + scenarioName);
            return false;
        }

        public bool TriggerChaos(string scenarioName) => InjectScenario(scenarioName);
        public bool TriggerScenario(string scenarioName) => InjectScenario(scenarioName);

        public void ResetAllScenarios()
        {
            if (_currentActiveScenario != null)
            {
                _currentActiveScenario.Revert();
                _currentActiveScenario = null;
                Debug.Log("[ChaosEngine] Reset active scenario.");
            }
        }
    }
}