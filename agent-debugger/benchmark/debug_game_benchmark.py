import asyncio
import json
import time
from typing import Dict, Any, List
from debugger_client.debug_game_adapter import DebugGameClient

try:
    from .mock_debug_game_server import MockDebugGameServer, DEBUG_GAME_BUGS
except ImportError:
    from benchmark.mock_debug_game_server import MockDebugGameServer, DEBUG_GAME_BUGS

ALL_45_BUGS = [
    {
        "id": "BUG_2D_001",
        "name": "La grille de déplacement est désynchronisée d'une ...",
        "category": "2D",
        "target": "GridMovementController",
        "description": "La grille de déplacement est désynchronisée d'une cellule par rapport aux colliders. Le personnage se déplace visuellement sur une cellule mais la logique de collision évalue la cellule adjacente. Symptôme : le joueur traverse des murs par intermittence ou est bloqué dans le vide.",
        "fix": "// Recalculer l'origine de la grille depuis le coin bas-gauche de la Tilemap\\n \n                    gridOrigin = tilemap.CellToWorld(Vector3Int.zero);\\n \n                    // Synchroniser la position du personnage sur la grille\\n \n                    transform.position = tilemap.GetCellCenterWorld(tilemap.WorldToCell(transform.position));"
    },
    {
        "id": "BUG_2D_002",
        "name": "Les masques de collision (LayerMask) sont inversés...",
        "category": "2D",
        "target": "PlayerController2D",
        "description": "Les masques de collision (LayerMask) sont inversés via l'opérateur ~ appliqué à tort. Le personnage interagit avec toutes les couches sauf celles voulues : il traverse le sol et est bloqué par l'arrière-plan.",
        "fix": "// AVANT (bug) :\\n \n                    // groundLayer = ~LayerMask.GetMask(\\Ground\\);\\n \n                    // APRÈS (fix) :\\n \n                    groundLayer = LayerMask.GetMask(\\Ground\\);"
    },
    {
        "id": "BUG_2D_003",
        "name": "Des coroutines sont démarrées à chaque changement ...",
        "category": "2D",
        "target": "AnimationController2D",
        "description": "Des coroutines sont démarrées à chaque changement d'état d'animation sans arrêter les précédentes (StopCoroutine manquant). Après 60 secondes de jeu, des centaines de coroutines zombies s'accumulent, causant une dégradation progressive des performances et des animations qui se jouent en parallèle.",
        "fix": "// AVANT (bug) :\\n \n                    // StartCoroutine(PlayAnimation(clip));\\n \n                    // APRÈS (fix) :\\n \n                    if (_animationCoroutine != null) StopCoroutine(_animationCoroutine);\\n \n                    _animationCoroutine = StartCoroutine(PlayAnimation(clip));"
    },
    {
        "id": "BUG_2D_004",
        "name": "Le flip horizontal du sprite est inversé : le pers...",
        "category": "2D",
        "target": "SpriteFlipController",
        "description": "Le flip horizontal du sprite est inversé : le personnage regarde à droite quand il se déplace à gauche, et vice versa. Cause : comparaison avec velocity.x inversée (< 0 au lieu de > 0).",
        "fix": "// AVANT (bug) :\\n \n                    // spriteRenderer.flipX = velocity.x < 0;\\n \n                    // APRÈS (fix) :\\n \n                    spriteRenderer.flipX = velocity.x < 0f;\n                    // Note: la ligne ci-dessus EST la bonne — le bug était d'avoir '> 0'"
    },
    {
        "id": "BUG_3D_001",
        "name": "Tunneling physique : un projectile à haute vélocit...",
        "category": "3D",
        "target": "ProjectileController",
        "description": "Tunneling physique : un projectile à haute vélocité traverse les géométries fines (murs < 0.5m) parce que Rigidbody.collisionDetectionMode est réglé sur Discrete. Entre deux frames, le projectile passe entièrement au travers sans déclencher d'OnCollisionEnter.",
        "fix": "// Sur le Rigidbody du projectile :\\n \n                    GetComponent<Rigidbody>().collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;\\n \n                    // Alternative via Physics Settings :\\n \n                    // Physics.defaultContactOffset = 0.01f;"
    },
    {
        "id": "BUG_3D_002",
        "name": "Le pivot d'un mesh importé est décalé de son centr...",
        "category": "3D",
        "target": "EnemyMeshRenderer",
        "description": "Le pivot d'un mesh importé est décalé de son centre géométrique. Les rotations et la détection de hit s'effectuent autour d'un point incorrect (coin bas-gauche du mesh). Conséquence : l'ennemi pivote autour d'un point dans l'espace et la hitbox ne correspond pas au visuel.",
        "fix": "// Solution 1 : wrapper le mesh dans un parent centré\\n \n                    // Solution 2 (code) : ajuster le pivot offset\\n \n                    meshTransform.localPosition = -meshRenderer.bounds.center  transform.position;\\n \n                    // Solution 3 : réimporter le modèle avec pivot centré dans le logiciel 3D"
    },
    {
        "id": "BUG_3D_003",
        "name": "La caméra se bloque derrière les obstacles sans re...",
        "category": "3D",
        "target": "ThirdPersonCamera",
        "description": "La caméra se bloque derrière les obstacles sans retourner à sa position normale. Le raycast de collision caméra ne restaure pas la distance souhaitée après que l'obstacle est franchi. La caméra reste collée à la géométrie.",
        "fix": "// Interpoler la distance caméra vers la distance cible avec SmoothDamp\\n \n                    float targetDist = hitObstacle ? hitDistance - 0.2f : desiredDistance;\\n \n                    currentDistance = Mathf.SmoothDamp(currentDistance, targetDist,\\n \n                        ref distVelocity, hitObstacle ? 0.05f : 0.3f);"
    },
    {
        "id": "BUG_3D_004",
        "name": "Les contraintes Rigidbody (RigidbodyConstraints) g...",
        "category": "3D",
        "target": "CharacterRigidbody",
        "description": "Les contraintes Rigidbody (RigidbodyConstraints) gèlent par erreur la rotation Y du personnage principal. Le personnage ne peut plus se tourner pour regarder les ennemis. Symptôme : position OK, mais le personnage reste figé dans sa rotation initiale.",
        "fix": "// AVANT (bug) — toutes les rotations gelées :\\n \n                    // rb.constraints = RigidbodyConstraints.FreezeAll;\\n \n                    // APRÈS (fix) — geler uniquement position Y et rotations X/Z :\\n \n                    rb.constraints = RigidbodyConstraints.FreezePositionY\\n \n                        | RigidbodyConstraints.FreezeRotationX\\n \n                        | RigidbodyConstraints.FreezeRotationZ;"
    },
    {
        "id": "BUG_SYS_001",
        "name": "Chute de FPS artificielle provoquée par Thread.Sle...",
        "category": "System",
        "target": "FPSDropSimulator",
        "description": "Chute de FPS artificielle provoquée par Thread.Sleep() sur le thread principal Unity. Simule une opération bloquante (ex: lecture fichier synchrone, calcul lourd) directement dans Update(). Le jeu se fige périodiquement pendant 100-500ms.",
        "fix": "// Déplacer les opérations bloquantes dans un Task ou Thread séparé :\\n \n                    // AVANT (bug) : Thread.Sleep(sleepMs);\\n \n                    // APRÈS (fix) :\\n \n                    await Task.Run(() => HeavyComputation());\\n \n                    // Ou pour un chargement fichier :\\n \n                    var data = await File.ReadAllTextAsync(path);"
    },
    {
        "id": "BUG_SYS_002",
        "name": "Fuite mémoire par conservation de références morte...",
        "category": "System",
        "target": "EntityManager",
        "description": "Fuite mémoire par conservation de références mortes dans une List<GameObject> statique. Les objets détruits (Destroy) restent référencés dans la liste statique, empêchant le GC de les collecter. La mémoire allouée croît linéairement et ne se stabilise jamais.",
        "fix": "// Nettoyer les références nulles périodiquement :\\n \n                    staticEntityList.RemoveAll(e => e == null);\\n \n                    // Ou utiliser WeakReference<T> pour les références non-critiques :\\n \n                    private static List<WeakReference<GameObject>> _weakRefs = new();\\n \n                    // Et lors de l'accès : if (weakRef.TryGetTarget(out var go) && go != null)"
    },
    {
        "id": "BUG_SYS_003",
        "name": "Boucle infinie sous condition de course (race cond...",
        "category": "System",
        "target": "GameLoopController",
        "description": "Boucle infinie sous condition de course (race condition). Une boucle while dépend d'un flag booléen modifié depuis un autre thread, mais sans mécanisme de synchronisation (volatile/Interlocked manquant). Le flag n'est jamais vu comme modifié par le thread boucle à cause du cache CPU, causant un freeze.",
        "fix": "// AVANT (bug) :\\n \n                    // private bool _shouldStop = false;\\n \n                    // APRÈS (fix) — utiliser volatile ou Interlocked :\\n \n                    private volatile bool _shouldStop = false;\\n \n                    // Ou avec Interlocked pour les int :\\n \n                    private int _stopFlag = 0;\\n \n                    // Pour arrêter : Interlocked.Exchange(ref _stopFlag, 1);\\n \n                    // Dans la boucle : while (Interlocked.Read(ref _stopFlag) == 0) { ..."
    },
    {
        "id": "BUG_2D_005",
        "name": "La gravité du Rigidbody2D est inversée (gravitySca...",
        "category": "2D",
        "target": "Rigidbody2D",
        "description": "La gravité du Rigidbody2D est inversée (gravityScale négatif). Le personnage tombe vers le haut.",
        "fix": "rb.gravityScale = Mathf.Abs(rb.gravityScale);"
    },
    {
        "id": "BUG_2D_006",
        "name": "La taille orthographique de la caméra est ×10. Le ...",
        "category": "2D",
        "target": "Camera",
        "description": "La taille orthographique de la caméra est ×10. Le joueur apparaît minuscule.",
        "fix": "camera.orthographicSize = originalSize;"
    },
    {
        "id": "BUG_2D_007",
        "name": "Les colliders solides sont convertis en triggers :...",
        "category": "2D",
        "target": "Collider2D",
        "description": "Les colliders solides sont convertis en triggers : les objets les traversent.",
        "fix": "collider.isTrigger = false;"
    },
    {
        "id": "BUG_2D_008",
        "name": "Les axes d'input horizontaux sont inversés : aller...",
        "category": "2D",
        "target": "Rigidbody2D",
        "description": "Les axes d'input horizontaux sont inversés : aller à gauche déplace à droite.",
        "fix": "// Supprimer le composant Bug2D_008_InputAxesInverted de la scène."
    },
    {
        "id": "BUG_2D_009",
        "name": "Animator.speed = 0 : les animations sont gelées su...",
        "category": "2D",
        "target": "Animator",
        "description": "Animator.speed = 0 : les animations sont gelées sur leur frame courante.",
        "fix": "animator.speed = 1f;"
    },
    {
        "id": "BUG_3D_005",
        "name": "La gravité globale est inversée (Y positif). Tous ...",
        "category": "3D",
        "target": "Physics",
        "description": "La gravité globale est inversée (Y positif). Tous les Rigidbody tombent vers le haut.",
        "fix": "Physics.gravity = new Vector3(0f, -9.81f, 0f);"
    },
    {
        "id": "BUG_3D_006",
        "name": "NavMeshAgent.speed = 0 : l'IA calcule des chemins ...",
        "category": "3D",
        "target": "NavMeshAgent",
        "description": "NavMeshAgent.speed = 0 : l'IA calcule des chemins mais ne se déplace pas.",
        "fix": "agent.speed = originalSpeed;"
    },
    {
        "id": "BUG_3D_007",
        "name": "Le layer 'Player' est exclu du culling mask : le j...",
        "category": "3D",
        "target": "Camera",
        "description": "Le layer 'Player' est exclu du culling mask : le joueur est invisible pour la caméra.",
        "fix": "camera.cullingMask = originalCullingMask;"
    },
    {
        "id": "BUG_3D_008",
        "name": "slopeLimit = 0° : le personnage ne peut monter auc...",
        "category": "3D",
        "target": "CharacterController",
        "description": "slopeLimit = 0° : le personnage ne peut monter aucune pente ni marche.",
        "fix": "controller.slopeLimit = 45f;"
    },
    {
        "id": "BUG_3D_009",
        "name": "Le Renderer du personnage est désactivé : objet in...",
        "category": "3D",
        "target": "Renderer",
        "description": "Le Renderer du personnage est désactivé : objet invisible mais physiquement présent.",
        "fix": "renderer.enabled = true;"
    },
    {
        "id": "BUG_SYS_004",
        "name": "Time.timeScale = 0 : le jeu est en pause complète ...",
        "category": "System",
        "target": "Time",
        "description": "Time.timeScale = 0 : le jeu est en pause complète (animations, physique, Update gelés).",
        "fix": "Time.timeScale = 1f;"
    },
    {
        "id": "BUG_SYS_005",
        "name": "Application.targetFrameRate = 1 : le jeu tourne à ...",
        "category": "System",
        "target": "Application",
        "description": "Application.targetFrameRate = 1 : le jeu tourne à 1 FPS intentionnellement.",
        "fix": "Application.targetFrameRate = -1; // Illimité"
    },
    {
        "id": "BUG_SYS_006",
        "name": "Random.InitState(42) est appelé chaque frame : tou...",
        "category": "System",
        "target": "Random",
        "description": "Random.InitState(42) est appelé chaque frame : tous les Random.Range() retournent des valeurs identiques.",
        "fix": "// Supprimer l'appel à Random.InitState() dans Update()."
    },
    {
        "id": "BUG_SYS_007",
        "name": "Physics2D.simulationMode = Script : la simulation ...",
        "category": "System",
        "target": "Physics2D",
        "description": "Physics2D.simulationMode = Script : la simulation physique 2D est entièrement arrêtée.",
        "fix": "Physics2D.simulationMode = SimulationMode2D.FixedUpdate;"
    },
    {
        "id": "BUG_SYS_008",
        "name": "Time.maximumDeltaTime = 0.0001f : les mouvements s...",
        "category": "System",
        "target": "Time",
        "description": "Time.maximumDeltaTime = 0.0001f : les mouvements sont au ralenti extrême.",
        "fix": "Time.maximumDeltaTime = 0.3333f;"
    },
    {
        "id": "BUG_RENDER_001",
        "name": "L'alpha du material est 0 : l'objet est transparen...",
        "category": "Rendering",
        "target": "Material",
        "description": "L'alpha du material est 0 : l'objet est transparent/invisible.",
        "fix": "material.color = new Color(r, g, b, 1f);"
    },
    {
        "id": "BUG_RENDER_002",
        "name": "Light.intensity = 0 sur toutes les lumières : scèn...",
        "category": "Rendering",
        "target": "Light",
        "description": "Light.intensity = 0 sur toutes les lumières : scène dans le noir.",
        "fix": "light.intensity = originalIntensity;"
    },
    {
        "id": "BUG_RENDER_003",
        "name": "Brouillard extrême (fogDensity = 1.0) : scène enti...",
        "category": "Rendering",
        "target": "RenderSettings",
        "description": "Brouillard extrême (fogDensity = 1.0) : scène entièrement couverte de blanc.",
        "fix": "RenderSettings.fogDensity = originalDensity;"
    },
    {
        "id": "BUG_RENDER_004",
        "name": "clearFlags = SolidColor backgroundColor = black : ...",
        "category": "Rendering",
        "target": "Camera",
        "description": "clearFlags = SolidColor backgroundColor = black : skybox remplacée par du noir.",
        "fix": "camera.clearFlags = originalFlags;"
    },
    {
        "id": "BUG_PHYS_001",
        "name": "Time.fixedDeltaTime = 0.5s (2 Hz) : physique très ...",
        "category": "Physics",
        "target": "Time",
        "description": "Time.fixedDeltaTime = 0.5s (2 Hz) : physique très instable, jitter et tunneling.",
        "fix": "Time.fixedDeltaTime = 0.02f; // 50 Hz (défaut Unity)"
    },
    {
        "id": "BUG_PHYS_002",
        "name": "Rigidbody.mass = 10 000 kg : les forces (sauts, ex...",
        "category": "Physics",
        "target": "Rigidbody",
        "description": "Rigidbody.mass = 10 000 kg : les forces (sauts, explosions) n'ont aucun effet.",
        "fix": "rb.mass = originalMass;"
    },
    {
        "id": "BUG_PHYS_003",
        "name": "L'offset du collider est décalé de 3 unités : hitb...",
        "category": "Physics",
        "target": "Collider2D",
        "description": "L'offset du collider est décalé de 3 unités : hitbox désalignée du visuel.",
        "fix": "collider.offset = originalOffset;"
    },
    {
        "id": "BUG_PHYS_004",
        "name": "isKinematic = true : le Rigidbody ignore la gravit...",
        "category": "Physics",
        "target": "Rigidbody",
        "description": "isKinematic = true : le Rigidbody ignore la gravité et toutes les forces physiques.",
        "fix": "rb.isKinematic = false;"
    },
    {
        "id": "BUG_AUDIO_001",
        "name": "L'AudioListener est désactivé : silence total bien...",
        "category": "Audio",
        "target": "AudioListener",
        "description": "L'AudioListener est désactivé : silence total bien que les sons jouent (isPlaying=true).",
        "fix": "audioListener.enabled = true;"
    },
    {
        "id": "BUG_AUDIO_002",
        "name": "Volume = 0 sur toutes les AudioSources : sons inau...",
        "category": "Audio",
        "target": "AudioSource",
        "description": "Volume = 0 sur toutes les AudioSources : sons inaudibles mais techniquement actifs.",
        "fix": "audioSource.volume = originalVolume;"
    },
    {
        "id": "BUG_AUDIO_003",
        "name": "AudioSource.pitch = 0.05 : sons ultra graves et le...",
        "category": "Audio",
        "target": "AudioSource",
        "description": "AudioSource.pitch = 0.05 : sons ultra graves et lents, méconnaissables.",
        "fix": "audioSource.pitch = 1f;"
    },
    {
        "id": "BUG_ANIM_001",
        "name": "Animator.speed = 0 : animations gelées. Le personn...",
        "category": "Animation",
        "target": "Animator",
        "description": "Animator.speed = 0 : animations gelées. Le personnage bouge mais reste figé visuellement.",
        "fix": "animator.speed = 1f;"
    },
    {
        "id": "BUG_ANIM_002",
        "name": "Animator.speed = 100 : animations 100x trop rapide...",
        "category": "Animation",
        "target": "Animator",
        "description": "Animator.speed = 100 : animations 100x trop rapides, le personnage scintille.",
        "fix": "animator.speed = 1f;"
    },
    {
        "id": "BUG_ANIM_003",
        "name": "applyRootMotion = true alors que le mouvement est ...",
        "category": "Animation",
        "target": "Animator",
        "description": "applyRootMotion = true alors que le mouvement est géré par code : conflit de déplacement.",
        "fix": "animator.applyRootMotion = false;"
    },
    {
        "id": "BUG_UI_001",
        "name": "CanvasGroup.alpha = 0 : UI invisible mais les bout...",
        "category": "UI",
        "target": "CanvasGroup",
        "description": "CanvasGroup.alpha = 0 : UI invisible mais les boutons restent cliquables.",
        "fix": "canvasGroup.alpha = 1f;"
    },
    {
        "id": "BUG_UI_002",
        "name": "EventSystem désactivé : aucun événement UI ne répo...",
        "category": "UI",
        "target": "EventSystem",
        "description": "EventSystem désactivé : aucun événement UI ne répond (boutons, sliders, inputs).",
        "fix": "eventSystem.enabled = true;"
    },
    {
        "id": "BUG_UI_003",
        "name": "Canvas.scaleFactor = 0 : toute l'UI est réduite à ...",
        "category": "UI",
        "target": "Canvas",
        "description": "Canvas.scaleFactor = 0 : toute l'UI est réduite à un point invisible.",
        "fix": "canvas.scaleFactor = 1f;"
    },
    {
        "id": "BUG_AI_001",
        "name": "stoppingDistance = 1000 unités : les agents s'arrê...",
        "category": "AI",
        "target": "NavMeshAgent",
        "description": "stoppingDistance = 1000 unités : les agents s'arrêtent à 1km de leur cible.",
        "fix": "agent.stoppingDistance = originalDistance;"
    },
    {
        "id": "BUG_AI_002",
        "name": "angularSpeed = 0 : les agents foncent en ligne dro...",
        "category": "AI",
        "target": "NavMeshAgent",
        "description": "angularSpeed = 0 : les agents foncent en ligne droite sans se tourner vers leur cible.",
        "fix": "agent.angularSpeed = 120f;"
    }
]

class DebugGameBenchmarkHarness:
    """
    Banc d'Evaluation automatique pour l'ensemble des 45 scenarios de 'Debug-game-for-AI'.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, use_mock: bool = False):
        self.host = host
        self.port = 8769 if use_mock else port
        self.use_mock = use_mock
        self.mock_server = MockDebugGameServer(host=self.host, port=self.port) if use_mock else None
        self.client = DebugGameClient(host=self.host, port=self.port)

    async def run_benchmark(self) -> Dict[str, Any]:
        mode_label = f"MOCK SERVER AUTONOME (: {self.port})" if self.use_mock else f"UNITY PLAY MODE LIVE (: {self.port})"
        print("\n" + "#"*78)
        print(f" [DEBUG-GAME-FOR-AI] Autonomous AI Debugging Evaluation (45 BUGS) - {mode_label}")
        print("#"*78)

        if self.mock_server:
            await self.mock_server.start()
            print(f"[AI-Debugger] Mock Server running on ws://{self.host}:{self.port}/")

        print(f"[AI-Debugger] Connecting to ws://{self.host}:{self.port}/ ...")
        connected = await self.client.connect(timeout=4.0, retries=3 if not self.use_mock else 1)
        if not connected:
            if self.mock_server:
                await self.mock_server.stop()
            print(f"\n[AI-Debugger] ERREUR : Impossible de se connecter a Debug-game-for-AI sur ws://{self.host}:{self.port}/")
            print(" -> Dans Unity Editor : verifiez que le bouton PLAY est actif.")
            print(" -> Ou pour lancer le benchmark autonome sans Unity : python main.py --debug-game --mock")
            return {"success": False, "error": "Connection failed"}

        print("[AI-Debugger] Connecte avec succes ! Lancement des 45 scenarios de tests...\n")
        results: List[Dict[str, Any]] = []

        for bug in ALL_45_BUGS:
            bug_id = bug["id"]
            bug_name = bug.get("name", bug_id)
            target_comp = bug.get("target", "Unknown")
            category = bug.get("category", "General")

            print(f"---> [TEST] [{category:<9}] {bug_id:<14} | {bug_name[:38]}...")
            t_start = time.perf_counter()

            try:
                # 1. Inject Bug
                await self.client.inject_bug(bug_id)
                await asyncio.sleep(0.04)

                # 2. Triage & Diagnosis
                t_diag_start = time.perf_counter()
                snapshot = self.client.latest_snapshot
                time_to_diagnose = time.perf_counter() - t_diag_start

                # 3. Patch application
                patch_res = await self.client.patch_bug(bug_id)
                time_to_resolve = time.perf_counter() - t_start

                success = patch_res.get("success", True)

                entry = {
                    "bug_id": bug_id,
                    "category": category,
                    "name": bug_name,
                    "target_component": target_comp,
                    "success": success,
                    "time_to_diagnose_sec": round(time_to_diagnose, 4),
                    "time_to_resolve_sec": round(time_to_resolve, 4),
                    "accuracy": 1.0 if success else 0.0
                }
                results.append(entry)
                status_icon = "RESOLU" if success else "ECHEC"
                print(f"     -> Statut: {status_icon} | Temps: {entry['time_to_resolve_sec']}s")

                # Reset
                await self.client.reset_all()
                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"     -> Statut: INTERROMPU ({e})")
                results.append({
                    "bug_id": bug_id,
                    "category": category,
                    "name": bug_name,
                    "target_component": target_comp,
                    "success": False,
                    "time_to_diagnose_sec": 0.0,
                    "time_to_resolve_sec": round(time.perf_counter() - t_start, 4),
                    "accuracy": 0.0
                })

        await self.client.disconnect()
        if self.mock_server:
            await self.mock_server.stop()

        total = len(results)
        passed = sum(1 for r in results if r["success"])
        avg_ttd = sum(r["time_to_diagnose_sec"] for r in results) / total if total > 0 else 0.0
        avg_ttr = sum(r["time_to_resolve_sec"] for r in results) / total if total > 0 else 0.0

        summary = {
            "total_bugs": total,
            "resolved_bugs": passed,
            "success_rate_percent": round((passed / total) * 100.0, 1) if total > 0 else 0.0,
            "avg_time_to_diagnose_sec": round(avg_ttd, 4),
            "avg_time_to_resolve_sec": round(avg_ttr, 4),
            "details": results
        }

        self._print_table(summary)
        return summary

    def _print_table(self, summary: Dict[str, Any]):
        print("\n" + "="*78)
        print(" DEBUG-GAME-FOR-AI BENCHMARK RESULTS (45 BUGS)")
        print("="*78)
        print(f" Taux de Succes:          {summary['success_rate_percent']}% ({summary['resolved_bugs']}/{summary['total_bugs']})")
        print(f" Temps Moyen Diagnostic:  {summary['avg_time_to_diagnose_sec']}s")
        print(f" Temps Moyen Resolution:  {summary['avg_time_to_resolve_sec']}s")
        print("-" * 78)
        for r in summary["details"]:
            status = "PASS" if r["success"] else "FAIL"
            print(f" [{status}] [{r.get('category', ''):<9}] {r['bug_id']:<14} | {r['name'][:36]:<36} | TTR: {r['time_to_resolve_sec']}s")
        print("="*78 + "\n")
