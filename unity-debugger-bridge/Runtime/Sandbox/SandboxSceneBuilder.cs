using System;
using UnityEngine;

namespace AIDebugger.Sandbox
{
    public static class SandboxSceneBuilder
    {
        public static void BuildProceduralSandbox()
        {
            var root = new GameObject("[Sandbox_Environment]");

            // 3D Ground
            var ground3D = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground3D.name = "Ground3D";
            ground3D.transform.position = Vector3.zero;
            ground3D.transform.localScale = new Vector3(5, 1, 5);
            ground3D.transform.SetParent(root.transform);

            // 3D Player
            var p3d = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            p3d.name = "Player3D";
            p3d.transform.position = new Vector3(0, 1, 0);
            var rb3d = p3d.AddComponent<Rigidbody>();
            rb3d.mass = 1f;
            var ctrl3d = p3d.AddComponent<Player3DController>();
            p3d.transform.SetParent(root.transform);

            // 3D Wall Obstacle
            var wall3D = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall3D.name = "Wall3D";
            wall3D.transform.position = new Vector3(0, 1, 5);
            wall3D.transform.localScale = new Vector3(10, 2, 0.2f);
            wall3D.AddComponent<PhysicsObstacle3D>();
            wall3D.transform.SetParent(root.transform);

            // 2D Entity root
            var root2D = new GameObject("Sandbox2D");
            root2D.transform.position = new Vector3(20, 0, 0);
            root2D.transform.SetParent(root.transform);

            var p2d = new GameObject("Player2D");
            p2d.transform.position = new Vector3(20, 1, 0);
            p2d.transform.SetParent(root2D.transform);
            var rb2d = p2d.AddComponent<Rigidbody2D>();
            var col2d = p2d.AddComponent<BoxCollider2D>();
            var ctrl2d = p2d.AddComponent<Player2DController>();

            // Setup SandboxManager
            var mgrObj = new GameObject("[SandboxManager]");
            var mgr = mgrObj.AddComponent<SandboxManager>();
            mgr.player3D = ctrl3d;
            mgr.player2D = ctrl2d;

            Debug.Log("[AIDebugger] Procedural sandbox built successfully.");
        }
    }
}