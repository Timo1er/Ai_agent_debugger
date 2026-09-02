using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Core
{
    [AddComponentMenu("AI Debugger/Physical Stress Lab")]
    public class PhysicalStressLab : MonoBehaviour
    {
        private static PhysicalStressLab _instance;
        public static PhysicalStressLab Instance => _instance;

        public bool IsRunningStressTest { get; private set; }
        public List<string> DetectedPhysicalFlaws = new List<string>();

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

        public void ExecuteCornerWedgeStress(GameObject player, float duration = 2.0f)
        {
            if (player != null)
                StartCoroutine(DoCornerWedge(player, duration));
        }

        private IEnumerator DoCornerWedge(GameObject player, float duration)
        {
            IsRunningStressTest = true;
            var cc = player.GetComponent<CharacterController>();
            Vector3 initPos = player.transform.position;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                if (cc != null && cc.enabled)
                {
                    // Forcer déplacement angulaire rapide
                    Vector3 wedgeDir = (player.transform.forward + player.transform.right).normalized;
                    cc.Move(wedgeDir * 20f * Time.deltaTime);
                }
                yield return null;
            }

            if (player.transform.position.y < -20f || float.IsNaN(player.transform.position.y))
            {
                DetectedPhysicalFlaws.Add($"Wedge Entrapment Tunneling à {player.transform.position}");
            }
            IsRunningStressTest = false;
        }

        public void ExecuteVelocityInversionStress(GameObject player, float duration = 1.5f)
        {
            if (player != null)
                StartCoroutine(DoVelocityInversion(player, duration));
        }

        private IEnumerator DoVelocityInversion(GameObject player, float duration)
        {
            IsRunningStressTest = true;
            var rb = player.GetComponent<Rigidbody>();
            var cc = player.GetComponent<CharacterController>();

            float elapsed = 0f;
            float dir = 1f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                dir *= -1f; // Inversion 60Hz

                if (rb != null && !rb.isKinematic)
                {
                    rb.SetLinearVelocity(player.transform.forward * dir * 25f);
                }
                else if (cc != null && cc.enabled)
                {
                    cc.Move(player.transform.forward * dir * 25f * Time.deltaTime);
                }
                yield return null;
            }

            IsRunningStressTest = false;
        }
    }
}