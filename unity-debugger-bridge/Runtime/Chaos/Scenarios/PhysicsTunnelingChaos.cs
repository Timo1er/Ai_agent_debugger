using System;
using UnityEngine;
using AIDebugger.Chaos;

namespace AIDebugger.Chaos.Scenarios
{
    public class PhysicsTunnelingChaos : ChaosScenarioBase
    {
        public override string ScenarioName => "physics_tunneling";
        public override string Description => "Injects extreme velocity into a projectile and disables continuous collision detection, resulting in collision penetration / tunneling.";

        private GameObject _projectile;
        private Vector3 _originalVelocity;
        private CollisionDetectionMode _originalDetectionMode;

        public override bool Inject(string parametersJson)
        {
            _projectile = GameObject.Find("ChaosProjectile") ?? GameObject.Find("Player3D") ?? GameObject.Find("Player2D");
            if (_projectile == null)
            {
                // Create a temporary chaos projectile
                _projectile = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                _projectile.name = "ChaosProjectile";
                _projectile.transform.position = new Vector3(0, 2, -10);
                var rb = _projectile.AddComponent<Rigidbody>();
                rb.mass = 1f;
            }

            var rb3d = _projectile.GetComponent<Rigidbody>();
            if (rb3d != null)
            {
                _originalVelocity = rb3d.velocity;
                _originalDetectionMode = rb3d.collisionDetectionMode;

                // Disable CCD (set to Discrete) and set ultra high velocity (500 units/s)
                rb3d.collisionDetectionMode = CollisionDetectionMode.Discrete;
                rb3d.velocity = new Vector3(0, 0, 500f);
                IsActive = true;
                return true;
            }

            var rb2d = _projectile.GetComponent<Rigidbody2D>();
            if (rb2d != null)
            {
                rb2d.collisionDetectionMode = CollisionDetectionMode2D.Discrete;
                rb2d.velocity = new Vector2(500f, 0);
                IsActive = true;
                return true;
            }

            return false;
        }

        public override void Revert()
        {
            if (_projectile != null)
            {
                var rb3d = _projectile.GetComponent<Rigidbody>();
                if (rb3d != null)
                {
                    rb3d.collisionDetectionMode = CollisionDetectionMode.Continuous;
                    rb3d.velocity = Vector3.zero;
                }
            }
            IsActive = false;
        }

        public override object GetStatus()
        {
            return new
            {
                targetObject = _projectile != null ? _projectile.name : "null",
                velocity = _projectile != null && _projectile.GetComponent<Rigidbody>() != null ? _projectile.GetComponent<Rigidbody>().velocity.magnitude : 0f,
                collisionMode = _projectile != null && _projectile.GetComponent<Rigidbody>() != null ? _projectile.GetComponent<Rigidbody>().collisionDetectionMode.ToString() : "none"
            };
        }
    }
}