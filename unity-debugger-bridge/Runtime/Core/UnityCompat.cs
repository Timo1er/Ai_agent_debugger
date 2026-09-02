using System;
using UnityEngine;
using Object = UnityEngine.Object;

namespace AIDebugger.Core
{
    /// <summary>
    /// Passerelle universelle de compatibilité multi-versions Unity (2020 / 2021 / 2022.3 LTS et Unity 6+).
    /// Garantit une compilation sans erreur et un comportement identique quelle que soit la version du moteur.
    /// </summary>
    public static class UnityCompat
    {
        public static Vector3 GetLinearVelocity(this Rigidbody rb)
        {
            if (rb == null) return Vector3.zero;
#if UNITY_6000_0_OR_NEWER
            return rb.linearVelocity;
#else
            return rb.velocity;
#endif
        }

        public static void SetLinearVelocity(this Rigidbody rb, Vector3 value)
        {
            if (rb == null) return;
#if UNITY_6000_0_OR_NEWER
            rb.linearVelocity = value;
#else
            rb.velocity = value;
#endif
        }

        public static Vector2 GetLinearVelocity(this Rigidbody2D rb)
        {
            if (rb == null) return Vector2.zero;
#if UNITY_6000_0_OR_NEWER
            return rb.linearVelocity;
#else
            return rb.velocity;
#endif
        }

        public static void SetLinearVelocity(this Rigidbody2D rb, Vector2 value)
        {
            if (rb == null) return;
#if UNITY_6000_0_OR_NEWER
            rb.linearVelocity = value;
#else
            rb.velocity = value;
#endif
        }

        public static T FindAny<T>() where T : Object
        {
#if UNITY_2023_1_OR_NEWER
            return Object.FindAnyObjectByType<T>();
#else
            return Object.FindObjectOfType<T>();
#endif
        }

        public static T[] FindAll<T>(bool includeInactive = false) where T : Object
        {
#if UNITY_2023_1_OR_NEWER
            return Object.FindObjectsByType<T>(includeInactive ? FindObjectsInactive.Include : FindObjectsInactive.Exclude, FindObjectsSortMode.None);
#else
            return Object.FindObjectsOfType<T>(includeInactive);
#endif
        }
    }
}