using AIDebugger.Core;
using System;
using System.Collections.Generic;
using UnityEngine;

namespace AIDebugger.Telemetry
{
    /// <summary>
    /// HUD et Visualiseur Graphique Temps Réel dans la vue Jeu & Scène Unity.
    /// Permet au développeur de voir exactement ce que l'agent IA et ses spécialistes analysent en direct.
    /// </summary>
    [AddComponentMenu("AI Debugger/AI Visual Overlay HUD")]
    [DefaultExecutionOrder(1000)]
    public class AIDebuggerOverlay : MonoBehaviour
    {
        private static AIDebuggerOverlay _instance;
        public static AIDebuggerOverlay Instance => _instance;

        [Header("Affichage HUD")]
        [SerializeField] private bool _showHUD = true;
        [SerializeField] private Color _themeColor = new Color(0.1f, 0.8f, 1f, 0.9f);
        [SerializeField] private Color _alertColor = new Color(1f, 0.25f, 0.25f, 0.95f);

        private string _currentAgent = "En Attente de Connexion...";
        private string _currentAction = "Superviseur en veille";
        private string _currentDetail = "Prêt pour l'audit";
        private bool _isAlert = false;
        private float _alertTimer = 0f;

        private readonly List<string> _recentFeed = new List<string>();
        private GUIStyle _boxStyle;
        private GUIStyle _titleStyle;
        private GUIStyle _feedStyle;
        private GUIStyle _metricStyle;

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

        public void SetStatus(string agentName, string action, string detail = "", bool isAlert = false)
        {
            _currentAgent = agentName ?? "Superviseur IA";
            _currentAction = action ?? "";
            _currentDetail = detail ?? "";
            _isAlert = isAlert;
            if (isAlert) _alertTimer = 3.0f;

            string timeStr = DateTime.Now.ToString("HH:mm:ss");
            string entry = $"[{timeStr}] <b>{_currentAgent}</b> : {_currentAction}";
            _recentFeed.Insert(0, entry);
            if (_recentFeed.Count > 6) _recentFeed.RemoveAt(_recentFeed.Count - 1);
        }

        private void Update()
        {
            if (_alertTimer > 0f)
            {
                _alertTimer -= Time.unscaledDeltaTime;
                if (_alertTimer <= 0f) _isAlert = false;
            }
        }

        private void OnGUI()
        {
            if (!_showHUD) return;

            InitStyles();

            float panelWidth = 420f;
            float panelHeight = 210f;
            float margin = 15f;

            Rect panelRect = new Rect(Screen.width - panelWidth - margin, margin, panelWidth, panelHeight);

            // Fond du panneau
            Color prevBg = GUI.backgroundColor;
            GUI.backgroundColor = _isAlert ? _alertColor : _themeColor;
            GUI.Box(panelRect, "", _boxStyle);
            GUI.backgroundColor = prevBg;

            GUILayout.BeginArea(new Rect(panelRect.x + 12, panelRect.y + 10, panelWidth - 24, panelHeight - 20));

            // En-tête HUD
            string statusIcon = _isAlert ? "⚠️ [ANOMALIE DÉTECTÉE]" : "🤖 [AI DEBUGGER SQUAD]";
            GUILayout.Label($"{statusIcon} <b>{_currentAgent.ToUpper()}</b>", _titleStyle);

            // Action courante
            GUILayout.Label($"<b>Action :</b> {_currentAction}", _metricStyle);
            if (!string.IsNullOrEmpty(_currentDetail))
            {
                GUILayout.Label($"<b>Détail :</b> {_currentDetail}", _metricStyle);
            }

            GUILayout.Space(6);
            GUILayout.Label("── <b>Journal d'Activité IA en Direct</b> ──", _metricStyle);

            // Fil d'actualité en direct
            foreach (var feed in _recentFeed)
            {
                GUILayout.Label(feed, _feedStyle);
            }

            GUILayout.EndArea();
        }

        private void InitStyles()
        {
            if (_boxStyle != null) return;

            _boxStyle = new GUIStyle(GUI.skin.box);
            Texture2D tex = new Texture2D(1, 1);
            tex.SetPixel(0, 0, new Color(0.05f, 0.08f, 0.12f, 0.88f));
            tex.Apply();
            _boxStyle.normal.background = tex;

            _titleStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 13,
                fontStyle = FontStyle.Bold,
                richText = true
            };
            _titleStyle.normal.textColor = Color.white;

            _metricStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 11,
                richText = true
            };
            _metricStyle.normal.textColor = new Color(0.9f, 0.95f, 1f, 0.95f);

            _feedStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 10,
                richText = true
            };
            _feedStyle.normal.textColor = new Color(0.7f, 0.85f, 0.95f, 0.85f);
        }

        private void OnDrawGizmos()
        {
            // Dessine les boîtes englobantes des entités trackées
            var rbs = UnityCompat.FindAll<Rigidbody>(false);
            foreach (var rb in rbs)
            {
                if (rb == null) continue;
                if (rb.transform.position.y < -20f)
                {
                    Gizmos.color = Color.red;
                    Gizmos.DrawWireCube(rb.transform.position, Vector3.one * 1.5f);
                }
                else
                {
                    Gizmos.color = new Color(0.2f, 0.8f, 1f, 0.4f);
                    Gizmos.DrawWireCube(rb.transform.position, Vector3.one * 0.8f);
                }
            }
        }
    }
}