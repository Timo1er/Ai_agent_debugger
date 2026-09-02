using System;
using UnityEngine;
using AIDebugger.Telemetry;

namespace AIDebugger.Sandbox
{
    [RequireComponent(typeof(Rigidbody2D))]
    public class Player2DController : MonoBehaviour
    {
        public float moveSpeed = 6f;
        public float jumpForce = 12f;
        public int health = 100;
        public bool isGrounded = true;
        public Transform targetTransform;

        private Rigidbody2D _rb;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
        }

        private void Update()
        {
            // Optional target tracking
            if (targetTransform != null)
            {
                float dir = Mathf.Sign(targetTransform.position.x - transform.position.x);
                _rb.velocity = new Vector2(dir * moveSpeed, _rb.velocity.y);
            }
        }

        private void OnCollisionEnter2D(Collision2D collision)
        {
            SpatialTracker.Instance?.RecordCollision(new Core.CollisionEventDto
            {
                timestamp = DateTime.UtcNow.ToString("o"),
                frame = Time.frameCount,
                type = "Collision2D",
                state = "Enter",
                sourceInstanceId = gameObject.GetHashCode(),
                sourceName = gameObject.name,
                targetInstanceId = collision.gameObject.GetHashCode(),
                targetName = collision.gameObject.name,
                impactVelocity = collision.relativeVelocity.magnitude,
                contactPointX = collision.contacts.Length > 0 ? collision.contacts[0].point.x : transform.position.x,
                contactPointY = collision.contacts.Length > 0 ? collision.contacts[0].point.y : transform.position.y
            });
        }
    }
}