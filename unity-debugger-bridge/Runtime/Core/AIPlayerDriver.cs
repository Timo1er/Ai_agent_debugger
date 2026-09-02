using AIDebugger.Core;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace AIDebugger.Core
{
    /// <summary>
    /// Pilote Autonome de Navigation & Exploration Physique pour Unity (FPS Microgame & Jeux 2D/3D).
    /// Dirige activement le joueur à travers le niveau, contourne les obstacles, sprinte, saute, tire
    /// et stresse les murs en continu.
    /// </summary>
    [AddComponentMenu("AI Debugger/AI Player Driver")]
    [DefaultExecutionOrder(100)]
    public class AIPlayerDriver : MonoBehaviour
    {
        private static AIPlayerDriver _instance;
        public static AIPlayerDriver Instance => _instance;

        [Header("État du Pilote IA")]
        public bool isAIDriving = false;
        public bool autoExploreLevel = true;
        public Vector3 aiMoveVector = Vector3.forward;
        public Vector2 aiLookVector = Vector2.zero;
        public bool aiJump = false;
        public bool aiSprint = true;

        private GameObject _playerObject;
        private CharacterController _characterController;
        private Rigidbody _rigidbody;
        private MonoBehaviour _fpsCharacterController;
        private PropertyInfo _charVelocityProp;
        private FieldInfo _charVelocityField;

        private float _turnCooldown = 0f;
        private float _fireCooldown = 0f;

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

        private void Start()
        {
            isAIDriving = true;
            autoExploreLevel = true;
            FindPlayer();
        }

        private void Update()
        {
            FindPlayer();

            if (_playerObject == null) return;

            if (autoExploreLevel)
            {
                DoAutonomousExplorationLogic();
            }

            if (isAIDriving)
            {
                ApplyPhysicalMovement();
            }
        }

        private void FindPlayer()
        {
            if (_playerObject != null && _playerObject.activeInHierarchy) return;

            // 1. Chercher par tag Player
            var p = GameObject.FindGameObjectWithTag("Player");
            if (p != null) { SetupPlayer(p); return; }

            // 2. Chercher par CharacterController
            var cc = AIDebugger.Core.UnityCompat.FindAny<CharacterController>();
            if (cc != null) { SetupPlayer(cc.gameObject); return; }

            // 3. Chercher par nom
            var named = GameObject.Find("Player") ?? GameObject.Find("PlayerCharacter");
            if (named != null) { SetupPlayer(named); }
        }

        private void SetupPlayer(GameObject p)
        {
            _playerObject = p;
            _characterController = p.GetComponent<CharacterController>();
            _rigidbody = p.GetComponent<Rigidbody>();

            // Reflection sur PlayerCharacterController (FPS Microgame)
            foreach (var mb in p.GetComponents<MonoBehaviour>())
            {
                if (mb != null && mb.GetType().Name == "PlayerCharacterController")
                {
                    _fpsCharacterController = mb;
                    _charVelocityProp = mb.GetType().GetProperty("CharacterVelocity");
                    _charVelocityField = mb.GetType().GetField("m_CharacterVelocity", BindingFlags.NonPublic | BindingFlags.Instance);
                    break;
                }
            }
            Debug.Log($"[AIPlayerDriver] Pilote IA attaché avec succès au Joueur : '{p.name}' !");
        }

        private void DoAutonomousExplorationLogic()
        {
            float dt = Time.deltaTime;
            _turnCooldown -= dt;
            _fireCooldown -= dt;

            // 1. Raycast de détection d'obstacles devant le joueur
            Vector3 origin = _playerObject.transform.position + Vector3.up * 0.8f;
            Vector3 forward = _playerObject.transform.forward;

            if (Physics.Raycast(origin, forward, out RaycastHit hit, 2.5f))
            {
                if (_turnCooldown <= 0f)
                {
                    // Tourner vers la gauche ou la droite
                    float turnAngle = (UnityEngine.Random.value > 0.5f ? 90f : -90f);
                    _playerObject.transform.Rotate(Vector3.up * turnAngle);
                    aiJump = true; // Essayer de sauter l'obstacle
                    _turnCooldown = 0.8f;
                }
            }
            else
            {
                aiJump = false;
                // Légère oscillation naturelle pour explorer la pièce
                _playerObject.transform.Rotate(Vector3.up * Mathf.Sin(Time.time * 1.5f) * 35f * dt);
            }

            // 2. Toujours avancer
            aiMoveVector = Vector3.forward;
            aiSprint = true;

            // 3. Tir périodique pour tester les armes
            if (_fireCooldown <= 0f)
            {
                TryFireWeapon();
                _fireCooldown = 3.0f;
            }
        }

        private void ApplyPhysicalMovement()
        {
            float speed = aiSprint ? 10f : 5f;
            Vector3 worldMove = _playerObject.transform.TransformDirection(aiMoveVector) * speed;
            if (aiJump) worldMove.y = 8f;

            // 1. Injection sur PlayerCharacterController (FPS Microgame)
            if (_fpsCharacterController != null)
            {
                if (_charVelocityProp != null && _charVelocityProp.CanWrite)
                {
                    _charVelocityProp.SetValue(_fpsCharacterController, worldMove, null);
                }
                else if (_charVelocityField != null)
                {
                    _charVelocityField.SetValue(_fpsCharacterController, worldMove);
                }
            }

            // 2. Déplacement physique direct sur CharacterController
            if (_characterController != null && _characterController.enabled)
            {
                Vector3 moveDelta = (worldMove + Vector3.down * 9.81f) * Time.deltaTime;
                _characterController.Move(moveDelta);
            }
            // 3. Déplacement sur Rigidbody
            else if (_rigidbody != null && !_rigidbody.isKinematic)
            {
                _rigidbody.SetLinearVelocity(new Vector3(worldMove.x, _rigidbody.GetLinearVelocity().y + (aiJump ? 6f : 0f), worldMove.z));
            }
            // 4. Déplacement transform direct
            else
            {
                _playerObject.transform.position += worldMove * Time.deltaTime;
            }
        }

        private void TryFireWeapon()
        {
            if (_playerObject == null) return;
            var weaponsManager = _playerObject.GetComponent("PlayerWeaponsManager");
            if (weaponsManager != null)
            {
                var method = weaponsManager.GetType().GetMethod("ShootWeapon", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (method != null)
                {
                    method.Invoke(weaponsManager, null);
                }
            }
        }

        public void DriveMove(float moveX, float moveZ, float yaw, bool sprint, bool jump, float duration)
        {
            StartCoroutine(DoDriveMove(moveX, moveZ, yaw, sprint, jump, duration));
        }

        private IEnumerator DoDriveMove(float moveX, float moveZ, float yaw, bool sprint, bool jump, float duration)
        {
            autoExploreLevel = false;
            isAIDriving = true;
            aiMoveVector = new Vector3(moveX, 0, moveZ).normalized;
            aiSprint = sprint;
            aiJump = jump;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                if (_playerObject != null && yaw != 0f)
                {
                    _playerObject.transform.Rotate(Vector3.up * yaw * 100f * Time.unscaledDeltaTime);
                }
                yield return null;
            }

            autoExploreLevel = true;
        }

        public void FuzzWallImpact(float duration = 3.0f)
        {
            StartCoroutine(DoFuzzWallImpact(duration));
        }

        private IEnumerator DoFuzzWallImpact(float duration)
        {
            autoExploreLevel = false;
            isAIDriving = true;
            aiSprint = true;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                aiMoveVector = Vector3.forward;
                aiJump = (Mathf.Sin(elapsed * 10f) > 0.3f);
                if (_playerObject != null)
                {
                    _playerObject.transform.Rotate(Vector3.up * Mathf.Sin(elapsed * 4f) * 45f * Time.unscaledDeltaTime);
                }
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }

            autoExploreLevel = true;
        }
    }
}