# Architecture Technique : Agent IA de Débogage & Copilote Unity (2D & 3D)

## 1. Topologie du Système

```
+-----------------------------------------------------------------------------------+
|                                  MOTEUR UNITY (C#)                                |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                            RuntimeInspector (Reflection)                    |  |
|  |  * Traversée hiérarchique récursive        * Inspection champs/propriétés   |  |
|  |  * Modification variables (SetMember)      * Invocation dynamique méthodes  |  |
|  +-----------------------------------------------------------------------------+  |
|                                         ^                                         |
|  +---------------------------+          |          +---------------------------+  |
|  |    TimeStepController     |          |          |   DynamicCodeEvaluator    |  |
|  |  * Time.timeScale pause   |          |          |  * Hot-Patching C#        |  |
|  |  * StepFrame frame-by-frame          |          |  * Snippet Execution      |  |
|  +---------------------------+          |          +---------------------------+  |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                       MainThreadDispatcher (Thread-Safe Queue)              |  |
|  +-----------------------------------------------------------------------------+  |
|                                         ^                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                   DebuggerServer (WebSocket / JSON-RPC 2.0)                 |  |
|  |  * Port TCP 8080 (RFC 6455)       * Streaming snapshots 5-30 Hz             |  |
|  +-----------------------------------------------------------------------------+  |
|                                         ^                                         |
|  +--------------------------------------+--------------------------------------+  |
|  |                                      |                                      |  |
|  v                                      v                                      v  |
| +--------------------+        +--------------------+        +--------------------+|
| |   LogInterceptor   |        |   SpatialTracker   |        | ProfilerCollector  ||
| | * Interception log |        | * Suivi 2D & 3D    |        | * FPS & Frame Time ||
| | * Stack traces     |        | * Collisions 2D/3D |        | * Mémoire GC / Heap||
| +--------------------+        +--------------------+        +--------------------+|
+-----------------------------------------|-----------------------------------------+
                                          |
                      WebSocket / JSON-RPC 2.0 (ws://127.0.0.1:8080)
                                          |
+-----------------------------------------v-----------------------------------------+
|                         SYSTÈME MULTI-AGENTS IA (PYTHON)                          |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                  UnityDebuggerClient (Async WebSocket Client)               |  |
|  +-----------------------------------------------------------------------------+  |
|                                         ^                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                   DebuggerOrchestrator (Superviseur Central)                |  |
|  +-----------------------------------------------------------------------------+  |
|         |                               |                               |         |
|         v                               v                               v         |
| +--------------------+        +--------------------+        +--------------------+|
| |    Triage Agent    |        |  Spatial Inspector |        |     Code Fixer     ||
| | * Analyse logs     |------->| * Inspecte mémoire |------->| * Stratégie patch  ||
| | * Détecte chutesFPS|        | * Collisions & CCD |        | * Exécute Hot-Fix  ||
| | * Isole anomalie   |        | * Cause racine     |        | * Vérifie santé    ||
| +--------------------+        +--------------------+        +--------------------+|
|                                         ^                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |          LLM Provider Engine (Gemini 1.5 Pro / GPT-4o / Heuristic Expert)   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Rôles et Spécialisations des Agents

### A. Agent Triage / Log Analyst
- **Mission** : Surveillance continue du flux télémétrique et classification immédiate des incidents.
- **Déclencheurs** :
  - Exceptions runtime non gérées (`NullReferenceException`, `IndexOutOfRangeException`).
  - Dégradation anormale du framerate (< 30 FPS).
  - Pic ou fuite continue de mémoire managée (`gcMemoryBytes` > 50 MB).
- **Livrable** : Rapport de triage avec niveau de sévérité, système suspecté et orientation d'enquête.

### B. Agent Inspecteur / Spatial Analyst
- **Mission** : Enquête structurelle et physique profonde sur la scène Unity.
- **Capacités** :
  - Parcours de la hiérarchie des `GameObjects` et de leurs composants.
  - Analyse des matrices physiques 2D (`Rigidbody2D`, `Collider2D`) et 3D (`Rigidbody`, `Collider`).
  - Lancer de rayons (`Raycast3D`), vérification des bounding boxes et détection des risques de traversée (tunneling).
- **Livrable** : Diagnostic de la cause racine identifiant l'objet, le composant et la variable défaillante.

### C. Agent Correcteur (Fixer / Patching)
- **Mission** : Formulation et application d'un correctif chirurgical.
- **Modes d'action** :
  - **Runtime Variable Override** : Modification immédiate d'un champ via `RuntimeInspector.SetMemberValue`.
  - **Dynamic C# Hot-Patching** : Exécution de scripts C# interprétés dynamiquement au runtime sans redémarrer la scène.
  - **State Reset & Component Control** : Réassignation de références et bascule d'états de composants.
- **Validation** : Surveillance post-patch (Health Check) pour certifier la stabilisation du framerate et l'arrêt des exceptions.

---

## 3. Moteur de Chaos (Sandboxing & Scénarios de Bugs)

Le `ChaosEngine` permet d'évaluer la résilience et l'efficacité de l'agent sur 5 types de dysfonctionnements récurrents :

1. **Physics Tunneling** : Projectile propulsé à haute vélocité avec détection discrète traversant les murs. L'agent détecte la vitesse excessive, active le mode continu (`Continuous Collision Detection`) et régule la vélocité.
2. **Memory Leak** : Allocation continue de textures et buffers non libérés. L'agent identifie l'explosion de la mémoire GC, déclenche la libération et le ramasse-miettes.
3. **NullReference Cascade** : Déréférencement brisant la boucle `Update()`. L'agent isole la variable `null` et lui réassigne dynamiquement une référence valide.
4. **Infinite Loop / Frame Drop Trap** : Boucle de calcul bloquante écrasant le framerate (< 5 FPS). L'agent localise la boucle, neutralise le compteur d'itérations et rétablit 60 FPS.
5. **Logic Race Condition** : Conflit d'états booléens (`isStunned` && `isAttacking`). L'agent déverrouille les flags et restaure la mobilité du joueur.