using System;
using UnityEngine;
using AIDebugger.Telemetry;

namespace AIDebugger.Sandbox
{
    [RequireComponent(typeof(Rigidbody))]
    public class Player3DController : MonoBehaviour
    {
        public float moveSpeed = 8f;
        public float jumpForce = 7f;
        public int health = 100;
        public bool isStunned = false;
        public bool isAttacking = false;
        public bool canMove = true;
        public Transform targetTransform;

        private Rigidbody _rb;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
        }

        private void Update()
        {
            if (!canMove || isStunned) return;

            // Simple movement pattern
            float h = Mathf.Sin(Time.time * 2f);
            float v = Mathf.Cos(Time.time * 2f);
            Vector3 move = new Vector3(h, 0, v).normalized * moveSpeed;
            _rb.velocity = new Vector3(move.x, _rb.velocity.y, move.z);
        }

        private void OnCollisionEnter(Collision collision)
        {
            SpatialTracker.Instance?.RecordCollision(new Core.CollisionEventDto
            {
                timestamp = DateTime.UtcNow.ToString("o"),
                frame = Time.frameCount,
                type = "Collision3D",
                state = "Enter",
                sourceInstanceId = gameObject.GetHashCode(),
                sourceName = gameObject.name,
                targetInstanceId = collision.gameObject.GetHashCode(),
                targetName = collision.gameObject.name,
                impactVelocity = collision.relativeVelocity.magnitude,
                contactPointX = collision.contacts.Length > 0 ? collision.contacts[0].point.x : transform.position.x,
                contactPointY = collision.contacts.Length > 0 ? collision.contacts[0].point.y : transform.position.y,
                contactPointZ = collision.contacts.Length > 0 ? collision.contacts[0].point.z : transform.position.z
            });
        }
    }
}