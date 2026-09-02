using System;
using UnityEngine;

namespace AIDebugger.Sandbox
{
    public class EnemyAI2D : MonoBehaviour
    {
        public float patrolRange = 5f;
        public float patrolSpeed = 2f;
        public bool isHostile = true;

        private Vector3 _startPos;

        private void Start()
        {
            _startPos = transform.position;
        }

        private void Update()
        {
            float offset = Mathf.PingPong(Time.time * patrolSpeed, patrolRange * 2) - patrolRange;
            transform.position = _startPos + new Vector3(offset, 0, 0);
        }
    }
}