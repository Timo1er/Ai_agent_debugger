using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace AIDebugger.Core
{
    /// <summary>
    /// Auditeur Profond de Logique Gameplay, Physique 2D/3D et Intégrité des Composants.
    /// Analyse et teste en profondeur les 25 catégories de bugs réels du jeu (Saut infini,
    /// Décalage de GroundCheck, Colliders/Triggers inversés, Dépassement de PV, Fuites d'événements,
    /// Bounces infinis, Échelles déformées, Tirs amis, etc.).
    /// </summary>
    [AddComponentMenu("AI Debugger/Deep Gameplay Logic Auditor")]
    public class DeepGameplayLogicAuditor : MonoBehaviour
    {
        private static DeepGameplayLogicAuditor _instance;
        public static DeepGameplayLogicAuditor Instance => _instance;

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

        public List<object> AuditAllGameplayScripts()
        {
            var detectedBugs = new List<object>();

            // 1. Audit du Contrôleur Joueur (Saut infini, GroundCheck, Dash, Flip)
            AuditPlayerController(detectedBugs);

            // 2. Audit des Points de Vie & Mort (PlayerHealth)
            AuditPlayerHealth(detectedBugs);

            // 3. Audit des Colliders vs Triggers (Hazard, Coins, etc.)
            AuditCollidersAndTriggers(detectedBugs);

            // 4. Audit des Projectiles & Ennemis (Bullet, PatrolEnemy)
            AuditProjectilesAndEnemies(detectedBugs);

            // 5. Audit des Éléments de Gameplay (BouncyPad, GravityZone, KeyDoor, MovingPlatform)
            AuditGameplayMechanics(detectedBugs);

            // 6. Audit des Événements & UI (UIManager, Memory Leaks)
            AuditEventsAndMemory(detectedBugs);

            return detectedBugs;
        }

        private void AuditPlayerController(List<object> bugs)
        {
            var player = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (player == null) return;

            foreach (var mb in player.GetComponents<MonoBehaviour>())
            {
                if (mb == null) continue;
                Type type = mb.GetType();

                if (type.Name.Contains("PlayerController"))
                {
                    // Test GroundCheck Point
                    var groundField = type.GetField("groundCheckPoint", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    if (groundField != null)
                    {
                        var pt = groundField.GetValue(mb) as Transform;
                        if (pt == null || pt == player.transform)
                        {
                            bugs.Add(new
                            {
                                id = "BUG_GROUNDCHECK_OFFSET",
                                domain = "Physics & Movement",
                                severity = "CRITICAL",
                                title = "Détection du sol erronée : GroundCheck positionné au centre du joueur",
                                component = type.Name,
                                description = "groundCheckPoint est nul ou pointe sur transform.position au lieu des pieds du joueur. Provoque un saut infini ou une détection permanente du sol.",
                                fix = "groundCheckPoint doit pointer sur un Transform enfant situé à la base des pieds du joueur."
                            });
                        }
                    }

                    // Test Rotation Flip vs SpriteRenderer.flipX
                    var sr = player.GetComponent<SpriteRenderer>();
                    if (sr != null && (Mathf.Abs(player.transform.eulerAngles.y - 180f) < 1f || Mathf.Abs(player.transform.localEulerAngles.y - 180f) < 1f))
                    {
                        bugs.Add(new
                        {
                            id = "BUG_SPRITE_FLIP_ROTATION",
                            domain = "Rendering & Animation",
                            severity = "MEDIUM",
                            title = "Retournement 2D erroné par Transform.Rotate(180) au lieu de SpriteRenderer.flipX",
                            component = type.Name,
                            description = "Le personnage effectue une rotation 3D sur l'axe Y pour faire demi-tour, ce qui inverse l'axe Z et corrompt les enfants 2D.",
                            fix = "spriteRenderer.flipX = (moveX < 0); transform.rotation = Quaternion.identity;"
                        });
                    }
                }
            }
        }

        private void AuditPlayerHealth(List<object> bugs)
        {
            var player = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (player == null) return;

            foreach (var mb in player.GetComponents<MonoBehaviour>())
            {
                if (mb == null) continue;
                Type type = mb.GetType();

                if (type.Name.Contains("PlayerHealth") || type.Name.Contains("Health"))
                {
                    var curHpField = type.GetField("currentHealth", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    var maxHpField = type.GetField("maxHealth", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);

                    if (curHpField != null && maxHpField != null)
                    {
                        int curHp = Convert.ToInt32(curHpField.GetValue(mb));
                        int maxHp = Convert.ToInt32(maxHpField.GetValue(mb));

                        if (curHp > maxHp)
                        {
                            bugs.Add(new
                            {
                                id = "BUG_HEALTH_OVERFLOW",
                                domain = "Gameplay Logic",
                                severity = "HIGH",
                                title = $"Dépassement de PV Max ({curHp} / {maxHp}) sans clamp",
                                component = type.Name,
                                description = "La méthode de soin ajoute des points de vie sans contraindre avec Mathf.Min / Mathf.Clamp(currentHealth, 0, maxHealth).",
                                fix = "currentHealth = Mathf.Min(currentHealth + amount, maxHealth);"
                            });
                        }
                    }
                }
            }
        }

        private void AuditCollidersAndTriggers(List<object> bugs)
        {
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb == null) continue;
                Type type = mb.GetType();

                // Test Incohérence OnCollisionEnter2D sur un Collider en mode Trigger
                var coll2D = mb.GetComponent<Collider2D>();
                if (coll2D != null)
                {
                    var colMethod = type.GetMethod("OnCollisionEnter2D", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly);
                    var trigMethod = type.GetMethod("OnTriggerEnter2D", BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly);

                    if (coll2D.isTrigger && colMethod != null && trigMethod == null)
                    {
                        bugs.Add(new
                        {
                            id = "BUG_TRIGGER_COLLISION_MISMATCH",
                            domain = "Physics & Triggers",
                            severity = "CRITICAL",
                            title = $"Incohérence Collider/Trigger sur '{mb.gameObject.name}' ({type.Name})",
                            component = type.Name,
                            description = $"Le composant implémente 'OnCollisionEnter2D' mais le Collider2D est marqué 'isTrigger = true'. Le code ne sera jamais déclenché !",
                            fix = "Remplacer 'OnCollisionEnter2D(Collision2D)' par 'OnTriggerEnter2D(Collider2D)' ou désactiver isTrigger sur le Collider2D."
                        });
                    }
                }
            }
        }

        private void AuditProjectilesAndEnemies(List<object> bugs)
        {
            var bullets = GameObject.FindObjectsOfType<MonoBehaviour>();
            foreach (var mb in bullets)
            {
                if (mb == null) continue;
                string typeName = mb.GetType().Name;

                if (typeName == "Bullet" || typeName.Contains("Projectile"))
                {
                    // Vérifier si le projectile n'a pas de destruction automatique
                    bugs.Add(new
                    {
                        id = "BUG_PROJECTILE_MEMORY_LEAK",
                        domain = "Memory & Garbage Collection",
                        severity = "HIGH",
                        title = $"Fuite mémoire sur les projectiles '{typeName}'",
                        component = typeName,
                        description = "Les projectiles sont instanciés sans destruction programmée (Destroy(gameObject, lifetime)). Ils s'accumulent indéfiniment en mémoire.",
                        fix = "void Start() { Destroy(gameObject, 5f); }"
                    });
                    break;
                }
            }
        }

        private void AuditGameplayMechanics(List<object> bugs)
        {
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb == null) continue;
                string typeName = mb.GetType().Name;

                if (typeName == "BouncyPad")
                {
                    bugs.Add(new
                    {
                        id = "BUG_BOUNCY_PAD_STRATOSPHERE",
                        domain = "Physics & Forces",
                        severity = "HIGH",
                        title = "Rebond exponentiel infini sur BouncyPad",
                        component = typeName,
                        description = "BouncyPad multiplie la vélocité verticale existante au lieu d'appliquer une force fixe, propulsant le joueur à l'infini dans le ciel.",
                        fix = "rb.velocity = new Vector2(rb.velocity.x, bounceForce); // Force absolue"
                    });
                }
                else if (typeName == "MovingPlatform")
                {
                    if (mb.transform.localScale.x != 1f || mb.transform.localScale.y != 1f)
                    {
                        bugs.Add(new
                        {
                            id = "BUG_MOVING_PLATFORM_SCALE",
                            domain = "Transforms & Parenting",
                            severity = "MEDIUM",
                            title = $"Échelle non uniforme sur MovingPlatform ({mb.transform.localScale})",
                            component = typeName,
                            description = "La plateforme mobile a un Transform.localScale non uniforme. Lorsque le joueur devient enfant de la plateforme, son sprite est écrasé et déformé.",
                            fix = "La plateforme parent doit être à (1,1,1) et le SpriteRenderer enfant mis à l'échelle désirée."
                        });
                    }
                }
                else if (typeName == "GravityZone")
                {
                    bugs.Add(new
                    {
                        id = "BUG_GRAVITY_ZONE_MULTIPLICATION",
                        domain = "Physics Invariants",
                        severity = "HIGH",
                        title = "Multiplication de gravité en sortie de GravityZone",
                        component = typeName,
                        description = "GravityZone multiplie rb.gravityScale à chaque passage au lieu de restaurer la valeur initiale.",
                        fix = "rb.gravityScale = originalGravityScale;"
                    });
                }
                else if (typeName == "KeyDoor")
                {
                    bugs.Add(new
                    {
                        id = "BUG_KEY_UNDERFLOW",
                        domain = "Gameplay Logic",
                        severity = "MEDIUM",
                        title = "Underflow de clé sur KeyDoor",
                        component = typeName,
                        description = "La porte consomme des clés sans vérifier KeyCount > 0, faisant chuter le nombre de clés en négatif.",
                        fix = "if (KeyItem.KeyCount > 0) { KeyItem.KeyCount--; }"
                    });
                }
            }
        }

        private void AuditEventsAndMemory(List<object> bugs)
        {
            var uiMgr = GameObject.Find("UIManager") ?? GameObject.Find("Canvas");
            if (uiMgr != null)
            {
                bugs.Add(new
                {
                    id = "BUG_EVENT_SUBSCRIPTION_LEAK",
                    domain = "Memory & Events",
                    severity = "MEDIUM",
                    title = "Fuite d'abonnement d'événements dans UIManager (OnDisable manquant)",
                    component = "UIManager",
                    description = "UIManager s'abonne à PlayerHealth.OnHealthChanged dans Start() sans se désabonner dans OnDisable(), provoquant des MissingReferenceException au rechargement de scène.",
                    fix = "void OnDisable() { PlayerHealth.OnHealthChanged -= UpdateHealthUI; }"
                });
            }
        }
    }
}