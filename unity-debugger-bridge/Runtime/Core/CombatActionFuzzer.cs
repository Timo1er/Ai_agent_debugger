using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Core
{
    [AddComponentMenu("AI Debugger/Combat Action Fuzzer")]
    public class CombatActionFuzzer : MonoBehaviour
    {
        private static CombatActionFuzzer _instance;
        public static CombatActionFuzzer Instance => _instance;

        public List<string> CombatAnomalies = new List<string>();

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

        public void FuzzWeaponStateCycle(GameObject player, float duration = 2.0f)
        {
            StartCoroutine(DoWeaponFuzz(player, duration));
        }

        private IEnumerator DoWeaponFuzz(GameObject player, float duration)
        {
            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                // Recherche d'armes actives
                var renderers = player != null ? player.GetComponentsInChildren<MeshRenderer>() : new MeshRenderer[0];
                int activeCount = 0;
                foreach (var r in renderers)
                {
                    if (r.enabled && r.gameObject.name.ToLower().Contains("weapon"))
                        activeCount++;
                }

                if (activeCount > 2)
                {
                    CombatAnomalies.Add($"Double arme superposée active ({activeCount} armes visibles)");
                }
                yield return new WaitForSeconds(0.2f);
            }
        }
    }
}