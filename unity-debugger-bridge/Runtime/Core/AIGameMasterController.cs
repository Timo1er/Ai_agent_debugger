using System;
using System.Collections;
using System.Reflection;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace AIDebugger.Core
{
    /// <summary>
    /// Contrôleur des Pouvoirs "Game Master / God Mode" de l'Agent IA.
    /// Donne à l'IA les pleins pouvoirs sur le jeu : Invulnérabilité (GodMode), Vol Libre (Fly / NoClip),
    /// Téléportation instantanée, Réinitialisation de niveau, Super Vitesse et Contrôle du Temps.
    /// </summary>
    [AddComponentMenu("AI Debugger/AI Game Master Controller")]
    [DefaultExecutionOrder(-50)]
    public class AIGameMasterController : MonoBehaviour
    {
        private static AIGameMasterController _instance;
        public static AIGameMasterController Instance => _instance;

        [Header("Pouvoirs Actifs")]
        public bool isGodMode = false;
        public bool isFlyMode = false;
        public float flyVerticalVelocity = 0f;
        public float customSpeedMultiplier = 1.0f;

        private GameObject _player;
        private Rigidbody2D _rb2d;
        private Rigidbody _rb3d;
        private CharacterController _cc;
        private MonoBehaviour _playerHealth;
        private FieldInfo _curHpField;
        private FieldInfo _maxHpField;
        private float _originalGravity2D = 1f;
        private bool _hasOriginalGravity = false;

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

        private void Update()
        {
            FindPlayer();

            if (_player == null) return;

            // 1. GOD MODE : Maintien constant des points de vie au maximum
            if (isGodMode && _playerHealth != null && _curHpField != null && _maxHpField != null)
            {
                try
                {
                    int maxHp = Convert.ToInt32(_maxHpField.GetValue(_playerHealth));
                    _curHpField.SetValue(_playerHealth, maxHp);
                }
                catch {}
            }

            // 2. FLY MODE (VOL LIBRE / NOCLIP)
            if (isFlyMode)
            {
                ApplyFlyMode();
            }
        }

        private void FindPlayer()
        {
            if (_player != null && _player.activeInHierarchy) return;

            _player = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (_player != null)
            {
                _rb2d = _player.GetComponent<Rigidbody2D>();
                _rb3d = _player.GetComponent<Rigidbody>();
                _cc = _player.GetComponent<CharacterController>();

                if (_rb2d != null && !_hasOriginalGravity)
                {
                    _originalGravity2D = _rb2d.gravityScale;
                    _hasOriginalGravity = true;
                }

                // Récupération de PlayerHealth
                foreach (var mb in _player.GetComponents<MonoBehaviour>())
                {
                    if (mb != null && (mb.GetType().Name.Contains("Health") || mb.GetType().Name.Contains("PlayerHealth")))
                    {
                        _playerHealth = mb;
                        _curHpField = mb.GetType().GetField("currentHealth", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                        _maxHpField = mb.GetType().GetField("maxHealth", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                        break;
                    }
                }
            }
        }

        private void ApplyFlyMode()
        {
            if (_rb2d != null)
            {
                _rb2d.gravityScale = 0f;
                float vy = flyVerticalVelocity != 0f ? flyVerticalVelocity : Mathf.Sin(Time.time * 2f) * 2f;
                _rb2d.SetLinearVelocity(new Vector2(_rb2d.GetLinearVelocity().x, vy));
            }
            else if (_rb3d != null)
            {
                _rb3d.useGravity = false;
                _rb3d.SetLinearVelocity(new Vector3(_rb3d.GetLinearVelocity().x, flyVerticalVelocity, _rb3d.GetLinearVelocity().z));
            }
            else if (_cc != null)
            {
                _cc.Move(Vector3.up * flyVerticalVelocity * Time.deltaTime);
            }
        }

        public void SetGodMode(bool enabled)
        {
            isGodMode = enabled;
            Debug.Log($"<color=yellow><b>[AI GAME MASTER]</b> God Mode : {(enabled ? "ACTIVÉ (Invulnérabilité totale)" : "DÉSACTIVÉ")}</color>");
            Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Game Master", $"GodMode: {(enabled ? "ON" : "OFF")}", enabled ? "Joueur Invulnérable" : "Physique standard");
        }

        public void SetFlyMode(bool enabled, float verticalSpeed = 0f)
        {
            isFlyMode = enabled;
            flyVerticalVelocity = verticalSpeed;

            if (!enabled && _rb2d != null && _hasOriginalGravity)
            {
                _rb2d.gravityScale = _originalGravity2D;
            }
            else if (!enabled && _rb3d != null)
            {
                _rb3d.useGravity = true;
            }

            Debug.Log($"<color=cyan><b>[AI GAME MASTER]</b> Vol Libre (Fly / NoClip) : {(enabled ? "ACTIVÉ" : "DÉSACTIVÉ")}</color>");
            Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Game Master", $"FlyMode: {(enabled ? "ON" : "OFF")}", enabled ? "Vol & Lévitation" : "Gravité standard");
        }

        public void TeleportPlayer(float x, float y, float z = 0f)
        {
            FindPlayer();
            if (_player == null) return;

            if (_cc != null) _cc.enabled = false;
            _player.transform.position = new Vector3(x, y, z);
            if (_rb2d != null) _rb2d.SetLinearVelocity(Vector2.zero);
            if (_rb3d != null) _rb3d.SetLinearVelocity(Vector3.zero);
            if (_cc != null) _cc.enabled = true;

            Debug.Log($"<color=magenta><b>[AI GAME MASTER]</b> Joueur téléporté à : ({x:F1}, {y:F1}, {z:F1})</color>");
            Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Game Master", "Téléportation", $"Position ({x:F1}, {y:F1})");
        }

        public void ResetLevel()
        {
            Debug.Log("<color=orange><b>[AI GAME MASTER]</b> Réinitialisation complète du Niveau...</color>");
            Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Game Master", "Reset Niveau", "Rechargement complet de la scène");
            int sceneIdx = SceneManager.GetActiveScene().buildIndex;
            if (sceneIdx >= 0)
            {
                SceneManager.LoadScene(sceneIdx);
            }
            else
            {
                SceneManager.LoadScene(SceneManager.GetActiveScene().name);
            }
        }
    }
}