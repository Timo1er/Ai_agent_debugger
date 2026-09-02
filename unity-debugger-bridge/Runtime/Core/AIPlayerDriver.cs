using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace AIDebugger.Core
{
    /// <summary>
    /// Pilote Physique & d'Exploration Active Autonome avec Pouvoirs Game Master.
    /// Utilise DE LUI-MÊME le GodMode (invulnérabilité), le Vol Libre (FlyMode)
    /// pour franchir les obstacles impossibles et la téléportation de stress.
    /// </summary>
    [AddComponentMenu("AI Debugger/AI Player Driver")]
    [DefaultExecutionOrder(100)]
    public class AIPlayerDriver : MonoBehaviour
    {
        private static AIPlayerDriver _instance;
        public static AIPlayerDriver Instance => _instance;

        [Header("État du Pilote IA")]
        public bool isAIDriving = false;
        public bool autoExploreLevel = false;
        public float aiHorizontalAxis = 1.0f;
        public bool aiJump = false;
        public bool aiDash = false;

        private GameObject _playerObject;
        private Rigidbody2D _rigidbody2D;
        private CharacterController _characterController;
        private Rigidbody _rigidbody;
        private bool _is2DGame = false;

        private MonoBehaviour _2dPlayerController;
        private FieldInfo _2dHorizontalInputField;
        private MethodInfo _2dJumpMethod;
        private MethodInfo _2dDashMethod;

        private MonoBehaviour _fpsCharacterController;
        private PropertyInfo _fpsCharVelocityProp;

        private float _turnCooldown = 0f;
        private float _jumpCooldown = 0f;
        private float _dashCooldown = 0f;
        private int _wallBlockCount = 0;

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
            FindPlayer();
        }

        private void Update()
        {
            FindPlayer();

            if (_playerObject == null) return;

            if (autoExploreLevel)
            {
                DoContinuousExplorationLoop();
            }

            if (isAIDriving)
            {
                ApplyMovementToPlayer();
            }
        }

        private void FindPlayer()
        {
            if (_playerObject != null && _playerObject.activeInHierarchy) return;

            var p = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (p != null) { SetupPlayer(p); return; }

            var rb2d = UnityCompat.FindAny<Rigidbody2D>();
            if (rb2d != null && (rb2d.gameObject.name.ToLower().Contains("player") || rb2d.CompareTag("Player")))
            {
                SetupPlayer(rb2d.gameObject);
                return;
            }

            var cc = UnityCompat.FindAny<CharacterController>();
            if (cc != null) { SetupPlayer(cc.gameObject); }
        }

        private void SetupPlayer(GameObject p)
        {
            _playerObject = p;
            _rigidbody2D = p.GetComponent<Rigidbody2D>();
            _characterController = p.GetComponent<CharacterController>();
            _rigidbody = p.GetComponent<Rigidbody>();

            _is2DGame = (_rigidbody2D != null || p.GetComponent<Collider2D>() != null);

            foreach (var mb in p.GetComponents<MonoBehaviour>())
            {
                if (mb == null) continue;
                Type t = mb.GetType();
                if (t.Name.Contains("PlayerController"))
                {
                    _2dPlayerController = mb;
                    _2dHorizontalInputField = t.GetField("horizontalInput", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    _2dJumpMethod = t.GetMethod("Jump", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    _2dDashMethod = t.GetMethod("Dash", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    break;
                }
                if (t.Name == "PlayerCharacterController")
                {
                    _fpsCharacterController = mb;
                    _fpsCharVelocityProp = t.GetProperty("CharacterVelocity");
                }
            }
            Debug.Log($"[AIPlayerDriver] Pilote IA attaché sur '{p.name}' (Mode {(_is2DGame ? "2D Platformer" : "3D")}) !");
        }

        private void DoContinuousExplorationLoop()
        {
            float dt = Time.deltaTime;
            _turnCooldown -= dt;
            _jumpCooldown -= dt;
            _dashCooldown -= dt;

            isAIDriving = true;

            if (_is2DGame)
            {
                Vector2 pos = _playerObject.transform.position;
                Vector2 dir = (aiHorizontalAxis >= 0) ? Vector2.right : Vector2.left;

                RaycastHit2D hit = Physics2D.Raycast(pos + Vector2.up * 0.2f, dir, 1.2f);
                if (hit.collider != null && !hit.collider.isTrigger && hit.collider.gameObject != _playerObject)
                {
                    _wallBlockCount++;

                    // POUVOIR AUTONOME : Si bloqué contre un grand mur, l'IA active le VOL de lui-même pour passer par-dessus !
                    if (_wallBlockCount > 3)
                    {
                        StartCoroutine(AutonomousFlightBoost(2.0f));
                        _wallBlockCount = 0;
                    }

                    if (_turnCooldown <= 0f)
                    {
                        aiHorizontalAxis = -aiHorizontalAxis;
                        _turnCooldown = 1.0f;

                        if (_jumpCooldown <= 0f)
                        {
                            aiJump = true;
                            _jumpCooldown = 0.6f;
                        }
                    }
                }
                else
                {
                    _wallBlockCount = 0;
                }

                if (_jumpCooldown <= 0f && UnityEngine.Random.value < 0.05f)
                {
                    aiJump = true;
                    _jumpCooldown = 1.2f;
                }

                if (_dashCooldown <= 0f && UnityEngine.Random.value < 0.03f)
                {
                    aiDash = true;
                    _dashCooldown = 2.0f;
                }
            }
            else
            {
                Vector3 origin = _playerObject.transform.position + Vector3.up * 0.8f;
                if (Physics.Raycast(origin, _playerObject.transform.forward, out RaycastHit hit, 2.5f))
                {
                    if (_turnCooldown <= 0f)
                    {
                        _playerObject.transform.Rotate(Vector3.up * (UnityEngine.Random.value > 0.5f ? 90f : -90f));
                        aiJump = true;
                        _turnCooldown = 0.8f;
                    }
                }
            }
        }

        private IEnumerator AutonomousFlightBoost(float duration)
        {
            Debug.Log("<color=cyan><b>[AI AUTONOMOUS POWER]</b> Obstacle élevé détecté : Activation autonome du Vol Libre (FlyMode) !</color>");
            AIGameMasterController.Instance?.SetFlyMode(true, 5.0f);
            yield return new WaitForSeconds(duration);
            AIGameMasterController.Instance?.SetFlyMode(false);
            Debug.Log("<color=cyan><b>[AI AUTONOMOUS POWER]</b> Atterrissage réussi au-delà de l'obstacle.</color>");
        }

        private void ApplyMovementToPlayer()
        {
            if (_playerObject == null) return;

            if (_is2DGame)
            {
                if (_2dPlayerController != null && _2dHorizontalInputField != null)
                {
                    _2dHorizontalInputField.SetValue(_2dPlayerController, aiHorizontalAxis);
                }

                if (_rigidbody2D != null)
                {
                    float speed = 8f;
                    float vx = aiHorizontalAxis * speed;
                    float vy = _rigidbody2D.GetLinearVelocity().y;

                    if (aiJump)
                    {
                        if (_2dJumpMethod != null)
                        {
                            _2dJumpMethod.Invoke(_2dPlayerController, null);
                        }
                        else
                        {
                            vy = 12f;
                        }
                        aiJump = false;
                    }

                    _rigidbody2D.SetLinearVelocity(new Vector2(vx, vy));
                }

                if (aiDash && _2dDashMethod != null)
                {
                    _2dDashMethod.Invoke(_2dPlayerController, null);
                    aiDash = false;
                }

                return;
            }

            Vector3 worldMove = _playerObject.transform.forward * 8f;
            if (aiJump) worldMove.y = 8f;

            if (_fpsCharacterController != null && _fpsCharVelocityProp != null)
            {
                _fpsCharVelocityProp.SetValue(_fpsCharacterController, worldMove, null);
            }
            if (_characterController != null && _characterController.enabled)
            {
                _characterController.Move((worldMove + Vector3.down * 9.81f) * Time.deltaTime);
            }
        }

        public void DriveMove(float moveX, float moveZ, float yaw, bool sprint, bool jump, float duration)
        {
            StartCoroutine(DoDriveMoveRoutine(moveX, moveZ, yaw, sprint, jump, duration));
        }

        private IEnumerator DoDriveMoveRoutine(float moveX, float moveZ, float yaw, bool sprint, bool jump, float duration)
        {
            isAIDriving = true;
            aiHorizontalAxis = moveX != 0 ? moveX : (moveZ != 0 ? moveZ : 1f);
            aiJump = jump;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }

            isAIDriving = false;
            aiHorizontalAxis = 0f;
            if (_2dPlayerController != null && _2dHorizontalInputField != null)
            {
                _2dHorizontalInputField.SetValue(_2dPlayerController, 0f);
            }
        }

        public void FuzzWallImpact(float duration = 3.0f)
        {
            StartCoroutine(DoFuzzWallImpactRoutine(duration));
        }

        private IEnumerator DoFuzzWallImpactRoutine(float duration)
        {
            isAIDriving = true;
            aiHorizontalAxis = 1.0f;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                aiJump = (Mathf.Sin(elapsed * 8f) > 0.4f);
                aiDash = (Mathf.Sin(elapsed * 4f) > 0.7f);
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }

            isAIDriving = false;
            aiHorizontalAxis = 0f;
            if (_2dPlayerController != null && _2dHorizontalInputField != null)
            {
                _2dHorizontalInputField.SetValue(_2dPlayerController, 0f);
            }
        }

        public void StartAutonomousExploration(float duration = 30f)
        {
            StopAllCoroutines();
            StartCoroutine(DoExplorationRoutine(duration));
        }

        private IEnumerator DoExplorationRoutine(float duration)
        {
            isAIDriving = true;
            autoExploreLevel = true;
            aiHorizontalAxis = 1.0f;

            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }

            autoExploreLevel = false;
            isAIDriving = false;
            if (_2dPlayerController != null && _2dHorizontalInputField != null)
            {
                _2dHorizontalInputField.SetValue(_2dPlayerController, 0f);
            }
        }
    }
}