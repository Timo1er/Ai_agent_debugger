using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace AIDebugger.Core
{
    [System.Serializable]
    public class UIElementDto
    {
        public string name;
        public string type;
        public string label;
        public bool isInteractable;
        public float screenX;
        public float screenY;
    }

    /// <summary>
    /// Opérateur Universel de Menus, UI Canvas et IMGUI (MainMenu, Pause, Choix de Niveaux).
    /// Permet à l'IA d'inspecter tous les boutons et de naviguer de façon transparente dans les menus du jeu.
    /// </summary>
    [AddComponentMenu("AI Debugger/AI Game Menu Operator")]
    public class AIGameMenuOperator : MonoBehaviour
    {
        private static AIGameMenuOperator _instance;
        public static AIGameMenuOperator Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = UnityCompat.FindAny<AIGameMenuOperator>();
                    if (_instance == null)
                    {
                        var srv = UnityCompat.FindAny<DebuggerServer>();
                        if (srv != null)
                        {
                            _instance = srv.gameObject.AddComponent<AIGameMenuOperator>();
                        }
                        else
                        {
                            var go = new GameObject("[AI-GameMenuOperator]");
                            _instance = go.AddComponent<AIGameMenuOperator>();
                            DontDestroyOnLoad(go);
                        }
                    }
                }
                return _instance;
            }
        }

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

        public List<UIElementDto> GetInteractiveElements()
        {
            var list = new List<UIElementDto>();

            // 1. Boutons du Menu Principal IMGUI (MainMenu)
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb != null && mb.GetType().Name == "MainMenu")
                {
                    list.Add(new UIElementDto { name = "Btn_Level1", type = "MainMenuButton", label = "🌲 Niveau 1 : Les Plaines Glitchées", isInteractable = true, screenX = 200, screenY = 100 });
                    list.Add(new UIElementDto { name = "Btn_Level2", type = "MainMenuButton", label = "🌌 Niveau 2 : La Caverne Inversée", isInteractable = true, screenX = 200, screenY = 150 });
                    list.Add(new UIElementDto { name = "Btn_Level3", type = "MainMenuButton", label = "👾 Niveau 3 : L'Arène du Glitch Boss", isInteractable = true, screenX = 200, screenY = 200 });
                    list.Add(new UIElementDto { name = "Btn_Options", type = "MainMenuButton", label = "⚙️ Options & Paramètres", isInteractable = true, screenX = 200, screenY = 250 });
                    list.Add(new UIElementDto { name = "Btn_Quit", type = "MainMenuButton", label = "❌ Quitter le jeu", isInteractable = true, screenX = 200, screenY = 300 });
                    break;
                }
            }

            // 2. Boutons UI Canvas UGUI standard
            var buttons = UnityCompat.FindAll<Button>(true);
            foreach (var btn in buttons)
            {
                if (btn == null) continue;
                string label = btn.gameObject.name;
                var textComp = btn.GetComponentInChildren<Text>();
                if (textComp != null && !string.IsNullOrEmpty(textComp.text))
                {
                    label = textComp.text;
                }

                Vector3 screenPos = Vector3.zero;
                var rt = btn.GetComponent<RectTransform>();
                if (rt != null) screenPos = rt.position;

                list.Add(new UIElementDto
                {
                    name = btn.gameObject.name,
                    type = "CanvasButton",
                    label = label,
                    isInteractable = btn.interactable && btn.gameObject.activeInHierarchy,
                    screenX = screenPos.x,
                    screenY = screenPos.y
                });
            }

            return list;
        }

        public bool ClickButtonByName(string buttonOrLabelName)
        {
            string target = (buttonOrLabelName ?? "").ToLower().Trim();

            // 1. Contrôle direct du MainMenu (IMGUI)
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb != null && mb.GetType().Name == "MainMenu")
                {
                    var closeMethod = mb.GetType().GetMethod("CloseMenu", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);

                    if (target.Contains("1") || target.Contains("plaine") || target.Contains("play") || target.Contains("start"))
                    {
                        closeMethod?.Invoke(mb, null);
                        LoadGameLevel(1);
                        Debug.Log("<color=cyan><b>[AI MENU OPERATOR]</b> Clic sur Menu : Lancement Niveau 1 !</color>");
                        Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Menu Operator", "Clic: Niveau 1", "Lancement des Plaines Glitchées");
                        return true;
                    }
                    if (target.Contains("2") || target.Contains("caverne"))
                    {
                        closeMethod?.Invoke(mb, null);
                        LoadGameLevel(2);
                        Debug.Log("<color=cyan><b>[AI MENU OPERATOR]</b> Clic sur Menu : Lancement Niveau 2 !</color>");
                        Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Menu Operator", "Clic: Niveau 2", "Lancement de la Caverne Inversée");
                        return true;
                    }
                    if (target.Contains("3") || target.Contains("boss") || target.Contains("arene"))
                    {
                        closeMethod?.Invoke(mb, null);
                        LoadGameLevel(3);
                        Debug.Log("<color=cyan><b>[AI MENU OPERATOR]</b> Clic sur Menu : Lancement Niveau 3 !</color>");
                        Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Menu Operator", "Clic: Niveau 3", "Lancement du Glitch Boss");
                        return true;
                    }
                    if (target.Contains("option") || target.Contains("setting"))
                    {
                        var showField = mb.GetType().GetField("showSettings", BindingFlags.NonPublic | BindingFlags.Instance);
                        showField?.SetValue(mb, true);
                        Debug.Log("<color=cyan><b>[AI MENU OPERATOR]</b> Clic sur Menu : Ouverture Options !</color>");
                        return true;
                    }
                    if (target.Contains("close") || target.Contains("resume"))
                    {
                        closeMethod?.Invoke(mb, null);
                        return true;
                    }
                }
            }

            // 2. Boutons Canvas UGUI
            var buttons = UnityCompat.FindAll<Button>(false);
            foreach (var btn in buttons)
            {
                if (btn == null) continue;
                string bName = btn.gameObject.name.ToLower();
                var textComp = btn.GetComponentInChildren<Text>();
                string bText = textComp != null ? textComp.text.ToLower() : "";

                if (bName.Contains(target) || bText.Contains(target))
                {
                    btn.onClick.Invoke();
                    Debug.Log($"<color=cyan><b>[AI MENU OPERATOR]</b> Clic déclenché sur '{btn.gameObject.name}' ({bText}) !</color>");
                    Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Menu Operator", $"Clic Bouton: '{btn.gameObject.name}'", "Action UI exécutée");
                    return true;
                }
            }

            return false;
        }

        public bool LoadGameLevel(int levelIndex)
        {
            // Fermer le MainMenu si ouvert
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb != null && mb.GetType().Name == "MainMenu")
                {
                    var closeMethod = mb.GetType().GetMethod("CloseMenu", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                    closeMethod?.Invoke(mb, null);
                }
            }

            // Charger via GameManager
            var gmObj = GameObject.Find("GameManager") ?? GameObject.Find("GameController");
            if (gmObj != null)
            {
                var gm = gmObj.GetComponent("GameManager");
                if (gm != null)
                {
                    var m = gm.GetType().GetMethod("LoadLevel");
                    if (m != null)
                    {
                        m.Invoke(gm, new object[] { levelIndex });
                        Time.timeScale = 1.0f;
                        Debug.Log($"<color=green><b>[AI MENU OPERATOR]</b> Niveau {levelIndex} chargé avec succès !</color>");
                        Telemetry.AIDebuggerOverlay.Instance?.SetStatus("Menu Operator", $"Chargement Niveau {levelIndex}", "Changement de niveau actif");
                        return true;
                    }
                }
            }

            // Charger via LevelBootstrapper
            var bootObj = GameObject.Find("LevelBootstrapper");
            if (bootObj != null)
            {
                var boot = bootObj.GetComponent("LevelBootstrapper");
                if (boot != null)
                {
                    var m = boot.GetType().GetMethod("BuildLevel", new Type[] { typeof(int) });
                    if (m != null)
                    {
                        m.Invoke(boot, new object[] { levelIndex });
                        Time.timeScale = 1.0f;
                        return true;
                    }
                }
            }

            return false;
        }
    }
}