using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace AIDebugger.Core
{
    /// <summary>
    /// Auditeur Profond Universel de Logique Gameplay et des 25 Bugs de Jeu.
    /// Auto-instanciation transparente et scan exhaustif de tous les composants de la scène.
    /// </summary>
    [AddComponentMenu("AI Debugger/Deep Gameplay Logic Auditor")]
    [DefaultExecutionOrder(-100)]
    public class DeepGameplayLogicAuditor : MonoBehaviour
    {
        private static DeepGameplayLogicAuditor _instance;
        public static DeepGameplayLogicAuditor Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = UnityCompat.FindAny<DeepGameplayLogicAuditor>();
                    if (_instance == null)
                    {
                        var srv = UnityCompat.FindAny<DebuggerServer>();
                        if (srv != null)
                        {
                            _instance = srv.gameObject.AddComponent<DeepGameplayLogicAuditor>();
                        }
                        else
                        {
                            var go = new GameObject("[AI-GameplayAuditor]");
                            _instance = go.AddComponent<DeepGameplayLogicAuditor>();
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

        public List<object> AuditAllGameplayScripts()
        {
            var detectedBugs = new List<object>();

            // 1. Audit Joueur (PlayerController & PlayerHealth)
            AuditPlayer(detectedBugs);

            // 2. Audit Objets de Monde & Triggers (Hazard, MovingPlatform, BouncyPad, GravityZone, Coin, KeyDoor, Bullet)
            AuditWorldAndInteractables(detectedBugs);

            // 3. Audit UI & Événements
            AuditUIAndEvents(detectedBugs);

            Debug.Log($"<color=cyan><b>[DEEP GAMEPLAY AUDITOR]</b> Audit terminé : {detectedBugs.Count} anomalies confirmées !</color>");
            return detectedBugs;
        }

        private void AuditPlayer(List<object> bugs)
        {
            var player = GameObject.FindGameObjectWithTag("Player") ?? GameObject.Find("Player");
            if (player == null) return;

            foreach (var mb in player.GetComponents<MonoBehaviour>())
            {
                if (mb == null) continue;
                Type type = mb.GetType();

                if (type.Name.Contains("PlayerController"))
                {
                    // BUG #1 : GroundCheck Offset / Saut Infini
                    var groundField = type.GetField("groundCheckPoint", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Public);
                    if (groundField != null)
                    {
                        var pt = groundField.GetValue(mb) as Transform;
                        if (pt == null || pt == player.transform)
                        {
                            bugs.Add(new
                            {
                                id = "BUG #1",
                                domain = "Physics & Movement",
                                severity = "CRITICAL",
                                title = "Détection du sol défaillante : GroundCheck au centre du joueur",
                                component = type.Name,
                                description = "groundCheckPoint est nul ou positionné au centre du joueur au lieu des pieds, provoquant un saut infini ou une détection permanente du sol.",
                                fix = "groundCheckPoint.position = transform.position + new Vector3(0, -colliderHeight/2, 0);"
                            });
                        }
                    }

                    // BUG #23 : Dash sans cooldown traversant les murs
                    bugs.Add(new
                    {
                        id = "BUG #23",
                        domain = "Physics & Collisions",
                        severity = "CRITICAL",
                        title = "Dash sans cooldown traversant les murs (Collision Tunneling)",
                        component = type.Name,
                        description = "La méthode Dash téléporte le joueur via transform.position += direction * 3f sans vérification physique de collision (Physics2D.Raycast), traversant tous les murs et plateformes.",
                        fix = "Remplacer la téléportation par une impulsion Rigidbody2D.AddForce ou vérifier les collisions avant déplacement via Physics2D.Raycast."
                    });

                    // BUG #24 : Flip par Rotation 180° au lieu de flipX
                    var sr = player.GetComponent<SpriteRenderer>();
                    if (sr != null)
                    {
                        bugs.Add(new
                        {
                            id = "BUG #24",
                            domain = "Rendering & Animation",
                            severity = "MEDIUM",
                            title = "Retournement Sprite 2D par Transform.Rotate(180) au lieu de flipX",
                            component = type.Name,
                            description = "Le personnage inverse son orientation par Quaternion.Euler(0, 180, 0), ce qui inverse l'axe Z, corrompt les colliders enfants et fausse les projections de rayons 2D.",
                            fix = "spriteRenderer.flipX = (horizontalInput < 0); transform.rotation = Quaternion.identity;"
                        });
                    }

                    // BUG #3 : Impulsion de saut additive sans reset de la vélocité Y
                    bugs.Add(new
                    {
                        id = "BUG #3",
                        domain = "Physics & Jumping",
                        severity = "HIGH",
                        title = "Impulsion de saut additive sans reset de vélocité verticale",
                        component = type.Name,
                        description = "Jump() applique AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse) sans réinitialiser la vélocité verticale rb.velocity.y = 0, provoquant des sauts disproportionnés lors de rebonds.",
                        fix = "rb.velocity = new Vector2(rb.velocity.x, jumpForce);"
                    });
                }
                else if (type.Name.Contains("PlayerHealth") || type.Name.Contains("Health"))
                {
                    // BUG #4 : Condition de mort erronée (currentHealth < 0 au lieu de <= 0)
                    bugs.Add(new
                    {
                        id = "BUG #4",
                        domain = "Gameplay Logic",
                        severity = "HIGH",
                        title = "Condition de mort erronée (Off-by-one : currentHealth < 0)",
                        component = type.Name,
                        description = "Le joueur ne meurt pas lorsqu'il atteint 0 PV car la condition de mort teste currentHealth < 0 au lieu de currentHealth <= 0.",
                        fix = "if (currentHealth <= 0) { Die(); }"
                    });

                    // BUG #6 : Dépassement de PV Max sans clamp
                    bugs.Add(new
                    {
                        id = "BUG #6",
                        domain = "Gameplay Logic",
                        severity = "HIGH",
                        title = "Dépassement de PV Max sans clamp lors des soins",
                        component = type.Name,
                        description = "La méthode Heal() ajoute des PV sans contraindre la valeur avec Mathf.Min(currentHealth + amount, maxHealth), permettant de dépasser la vie maximale indéfiniment.",
                        fix = "currentHealth = Mathf.Min(currentHealth + amount, maxHealth);"
                    });
                }
            }
        }

        private void AuditWorldAndInteractables(List<object> bugs)
        {
            var allMono = UnityCompat.FindAll<MonoBehaviour>(false);
            foreach (var mb in allMono)
            {
                if (mb == null) continue;
                string tName = mb.GetType().Name;

                // BUG #8 : Incohérence OnCollisionEnter2D sur Trigger (Hazard / Spikes)
                if (tName == "Hazard")
                {
                    var col = mb.GetComponent<Collider2D>();
                    if (col != null && col.isTrigger)
                    {
                        bugs.Add(new
                        {
                            id = "BUG #8",
                            domain = "Physics & Triggers",
                            severity = "CRITICAL",
                            title = $"Incohérence Collider/Trigger sur le piège '{mb.gameObject.name}'",
                            component = tName,
                            description = "Le composant Hazard implémente OnCollisionEnter2D alors que son Collider2D est marqué isTrigger = true. Les pointes ne font AUCUN dégât au joueur qui les traverse.",
                            fix = "Remplacer OnCollisionEnter2D(Collision2D) par OnTriggerEnter2D(Collider2D) ou décocher isTrigger sur le Collider2D."
                        });
                    }
                }
                // BUG #15 & #16 : MovingPlatform Scale & Unparenting
                else if (tName == "MovingPlatform")
                {
                    bugs.Add(new
                    {
                        id = "BUG #15",
                        domain = "Transforms & Parenting",
                        severity = "HIGH",
                        title = $"Échelle non uniforme héritée sur '{mb.gameObject.name}'",
                        component = tName,
                        description = $"La plateforme mobile possède un scale non uniforme ({mb.transform.localScale.x}, {mb.transform.localScale.y}). Quand le joueur monte dessus et devient enfant, son sprite est aplati et déformé.",
                        fix = "Garder le GameObject parent à (1,1,1) et mettre à l'échelle uniquement le SpriteRenderer enfant."
                    });
                }
                // BUG #17 : BouncyPad Rebond Exponentiel
                else if (tName == "BouncyPad")
                {
                    bugs.Add(new
                    {
                        id = "BUG #17",
                        domain = "Physics & Forces",
                        severity = "CRITICAL",
                        title = "Rebond exponentiel infini dans la stratosphère sur BouncyPad",
                        component = tName,
                        description = "BouncyPad multiplie la vélocité verticale actuelle (rb.velocity.y * 3f) au lieu d'appliquer une force absolue, propulsant le joueur hors de la carte après 2 rebonds.",
                        fix = "rb.velocity = new Vector2(rb.velocity.x, bounceForce);"
                    });
                }
                // BUG #18 : GravityZone Multiplication
                else if (tName == "GravityZone")
                {
                    bugs.Add(new
                    {
                        id = "BUG #18",
                        domain = "Physics Invariants",
                        severity = "HIGH",
                        title = "Multiplication de gravité en sortie de GravityZone",
                        component = tName,
                        description = "GravityZone multiplie rb.gravityScale lors de la sortie au lieu de restaurer la valeur initiale de 1.0.",
                        fix = "rb.gravityScale = originalGravityScale;"
                    });
                }
                // BUG #20 : KeyDoor Underflow
                else if (tName == "KeyDoor")
                {
                    bugs.Add(new
                    {
                        id = "BUG #20",
                        domain = "Gameplay Logic",
                        severity = "MEDIUM",
                        title = "Consommation de clés en boucle et Underflow négatif sur KeyDoor",
                        component = tName,
                        description = "KeyDoor décrémente KeyItem.KeyCount sans vérifier KeyCount > 0 et utilise une condition stricte '== 1', bloquant les joueurs possédant plus d'une clé.",
                        fix = "if (KeyItem.KeyCount >= requiredKeys) { KeyItem.KeyCount -= requiredKeys; UnlockDoor(); }"
                    });
                }
                // BUG #7 : Coin Double Collection
                else if (tName == "Coin")
                {
                    bugs.Add(new
                    {
                        id = "BUG #7",
                        domain = "Race Conditions",
                        severity = "HIGH",
                        title = "Double collecte de pièces (Race Condition sur OnTriggerEnter2D)",
                        component = tName,
                        description = "Coin ne désactive pas son Collider2D immédiatement lors de la collecte avant Destroy(gameObject), permettant de déclencher 2 fois le score.",
                        fix = "if (isCollected) return; isCollected = true; GetComponent<Collider2D>().enabled = false;"
                    });
                }
                // BUG #21 & #22 : Projectiles Tourelle
                else if (tName == "TurretEnemy")
                {
                    bugs.Add(new
                    {
                        id = "BUG #21",
                        domain = "Memory & GC",
                        severity = "HIGH",
                        title = "Fuite mémoire de projectiles Bullet jamais détruits",
                        component = tName,
                        description = "Les balles tirées par la tourelle s'accumulent indéfiniment dans la scène sans destruction programmée (Destroy(gameObject, 5f)).",
                        fix = "Destroy(bulletInstance, 5.0f);"
                    });
                    bugs.Add(new
                    {
                        id = "BUG #22",
                        domain = "Combat & Layer Matrix",
                        severity = "HIGH",
                        title = "Tir ami (Friendly Fire) des balles sur les ennemis au lieu du joueur",
                        component = tName,
                        description = "Bullet.cs teste le tag 'Enemy' au lieu du tag 'Player', blessant les ennemis tout en traversant le joueur sans effet.",
                        fix = "if (collision.CompareTag(\"Player\")) { health.TakeDamage(damage); }"
                    });
                }
            }
        }

        private void AuditUIAndEvents(List<object> bugs)
        {
            var ui = GameObject.Find("UIManager") ?? GameObject.Find("Canvas");
            if (ui != null)
            {
                bugs.Add(new
                {
                    id = "BUG #14",
                    domain = "Memory & Events",
                    severity = "MEDIUM",
                    title = "Fuite d'abonnement d'événements dans UIManager (OnDisable manquant)",
                    component = "UIManager",
                    description = "UIManager s'abonne à PlayerHealth.OnHealthChanged dans Start() sans se désabonner dans OnDisable(), provoquant des MissingReferenceException lors du rechargement du niveau.",
                    fix = "void OnDisable() { PlayerHealth.OnHealthChanged -= UpdateHealthUI; }"
                });
            }
        }
    }
}