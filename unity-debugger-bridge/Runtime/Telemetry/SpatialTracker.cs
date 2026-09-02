#pragma warning disable CS0619
using System;
using System.Collections.Generic;
using UnityEngine;
using AIDebugger.Core;

namespace AIDebugger.Telemetry
{
    public class SpatialTracker : MonoBehaviour
    {
        private static SpatialTracker _instance;
        public static SpatialTracker Instance => _instance;

        private const int MaxCollisionHistory = 100;
        private readonly List<CollisionEventDto> _recentCollisions = new List<CollisionEventDto>();
        private readonly object _collisionLock = new object();

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

        public void RecordCollision(CollisionEventDto ev)
        {
            lock (_collisionLock)
            {
                _recentCollisions.Add(ev);
                if (_recentCollisions.Count > MaxCollisionHistory)
                {
                    _recentCollisions.RemoveAt(0);
                }
            }
            DebuggerServer.Instance?.BroadcastNotification("telemetry.collisionEvent", ev);
        }

        public List<CollisionEventDto> GetRecentCollisions(int count = 20)
        {
            lock (_collisionLock)
            {
                int take = Math.Min(count, _recentCollisions.Count);
                int start = _recentCollisions.Count - take;
                return _recentCollisions.GetRange(start, take);
            }
        }

        public List<SpatialEntity2D> GetSnapshot2D()
        {
            var list = new List<SpatialEntity2D>();
            var rbs2D = FindObjectsOfType<Rigidbody2D>(false);
            foreach (var rb in rbs2D)
            {
                var go = rb.gameObject;
                var col = go.GetComponent<Collider2D>();
                var ent = new SpatialEntity2D
                {
                    instanceId = go.GetHashCode(),
                    name = go.name,
                    tag = go.tag,
                    layer = go.layer,
                    activeInHierarchy = go.activeInHierarchy,
                    posX = go.transform.position.x,
                    posY = go.transform.position.y,
                    rotationZ = go.transform.eulerAngles.z,
                    scaleX = go.transform.localScale.x,
                    scaleY = go.transform.localScale.y,
                    velocityX = rb.GetLinearVelocity().x,
                    velocityY = rb.GetLinearVelocity().y,
                    angularVelocity = rb.angularVelocity,
                    hasCollider2D = col != null,
                    isTrigger = col != null && col.isTrigger
                };

                if (col != null)
                {
                    ent.boundsMinX = col.bounds.min.x;
                    ent.boundsMinY = col.bounds.min.y;
                    ent.boundsMaxX = col.bounds.max.x;
                    ent.boundsMaxY = col.bounds.max.y;
                }
                list.Add(ent);
            }
            return list;
        }

        public List<SpatialEntity3D> GetSnapshot3D()
        {
            var list = new List<SpatialEntity3D>();
            var rbs3D = FindObjectsOfType<Rigidbody>(false);
            foreach (var rb in rbs3D)
            {
                var go = rb.gameObject;
                var col = go.GetComponent<Collider>();
                var ent = new SpatialEntity3D
                {
                    instanceId = go.GetHashCode(),
                    name = go.name,
                    tag = go.tag,
                    layer = go.layer,
                    activeInHierarchy = go.activeInHierarchy,
                    posX = go.transform.position.x,
                    posY = go.transform.position.y,
                    posZ = go.transform.position.z,
                    rotX = go.transform.rotation.x,
                    rotY = go.transform.rotation.y,
                    rotZ = go.transform.rotation.z,
                    rotW = go.transform.rotation.w,
                    scaleX = go.transform.localScale.x,
                    scaleY = go.transform.localScale.y,
                    scaleZ = go.transform.localScale.z,
                    velocityX = rb.GetLinearVelocity().x,
                    velocityY = rb.GetLinearVelocity().y,
                    velocityZ = rb.GetLinearVelocity().z,
                    angularVelocityX = rb.angularVelocity.x,
                    angularVelocityY = rb.angularVelocity.y,
                    angularVelocityZ = rb.angularVelocity.z,
                    hasCollider = col != null,
                    isTrigger = col != null && col.isTrigger
                };

                if (col != null)
                {
                    ent.boundsMinX = col.bounds.min.x;
                    ent.boundsMinY = col.bounds.min.y;
                    ent.boundsMinZ = col.bounds.min.z;
                    ent.boundsMaxX = col.bounds.max.x;
                    ent.boundsMaxY = col.bounds.max.y;
                    ent.boundsMaxZ = col.bounds.max.z;
                }
                list.Add(ent);
            }
            return list;
        }
    }
}