# AI Agent Universal Debugger & Telemetry Bridge for Unity (2D & 3D)

Copilote de débogage autonome et outil d'inspection universel pour jeux vidéo Unity (2D et 3D), combinant un bridge de télémétrie C# haute performance et une architecture multi-agents IA.

---

## Fonctionnalités Clés

- **Serveur de Communication Temps Réel (Unity -> IA)** : Serveur WebSocket asynchrone natif C# (JSON-RPC 2.0) avec file d'exécution thread-safe (`MainThreadDispatcher`).
- **Télémétrie Complète** :
  - **Arbre Hiérarchique & Réflexion** : Exploration complète des GameObjects, composants et membres privés/publics.
  - **Champs Spatiaux 2D & 3D** : Positions, vélocités `Rigidbody`/`Rigidbody2D`, bounding boxes, lancers de rayons (`Raycast3D`), événements de collision.
  - **Logs & Stack Traces** : Interception continue des logs, warnings et exceptions avec piles d'appels.
  - **Profiler & Métriques** : Suivi du framerate (FPS), frame time, mémoire allouée/GC, compteurs d'objets.
- **Contrôle du Time Step** : Pause, reprise, modification de `Time.timeScale` et pas-à-pas frame-by-frame (`StepFrames`).
- **Architecture Multi-Agents IA (Python)** :
  - **Triage / Log Analyst Agent** : Détection des anomalies et isolation du composant incriminé.
  - **Inspector / Spatial Analyst Agent** : Analyse spatiale, vérification des colliders/CCD et inspection mémoire/champs.
  - **Fixer / Hot-Patch Agent** : Élaboration de correctifs runtime et déploiement de patchs C# dynamiques.
  - **Debugger Orchestrator** : Superviseur coordonnant la boucle détection -> diagnostic -> patch -> vérification de santé.
- **Moteur de Chaos & Scène Sandbox (2D & 3D)** :
  - Scénarios types : *Physics Tunneling*, *Memory Leak*, *NullReference Cascade*, *Logic Race Condition*, *Infinite Loop Hang Trap*.
- **Banc d'Évaluation Automatisé (Benchmark Harness)** : Mesure du TTD (Time To Diagnose), TTR (Time To Resolve), précision diagnostique et rétablissement du jeu.

---

## Résultats du Banc d'Évaluation (Benchmark)

```
======================================================================
 BENCHMARK EVALUATION RESULTS SUMMARY
======================================================================
 Success Rate:            100.0% (5/5)
 Avg Diagnostic Accuracy: 100.0%
 Avg Time to Diagnose:     0.0001s
 Avg Time to Resolve:      0.3092s
----------------------------------------------------------------------
 [PASS] NullReference Crash Cascade         | TTD: 0.0004s | TTR: 0.3122s | Acc: 100%
 [PASS] Physics Tunneling & CCD Failure     | TTD: 0.0000s | TTR: 0.3136s | Acc: 100%
 [PASS] Catastrophic Memory Surge           | TTD: 0.0001s | TTR: 0.3100s | Acc: 100%
 [PASS] Infinite Loop Frame Drop (<5 FPS)   | TTD: 0.0001s | TTR: 0.3136s | Acc: 100%
 [PASS] Logic State Machine Stalemate       | TTD: 0.0001s | TTR: 0.2968s | Acc: 100%
======================================================================
```

---

## Structure du Répertoire

```
AI-agent-debugger/
├── unity-debugger-bridge/       # Module Unity C# (UPM Package)
│   ├── package.json             # Manifeste du package Unity
│   └── Runtime/
│       ├── Core/                # Serveur WebSocket, Reflection, TimeStep, Hot-Patching
│       ├── Telemetry/           # Logs, Métriques Profiler, Spatial 2D/3D
│       ├── Chaos/               # Moteur de Chaos & 5 scénarios de bugs
│       └── Sandbox/             # Contrôleurs 2D/3D & Constructeur de scène
├── agent-debugger/              # Système Multi-Agents IA (Python)
│   ├── debugger_client/         # Client WebSocket & Protocole JSON-RPC
│   ├── agents/                  # Triage, Spatial Inspector, Code Fixer, Orchestrator
│   ├── llm/                     # Providers LLM (Gemini, OpenAI, Heuristic Expert)
│   ├── benchmark/               # Serveur Mock Unity & Banc d'évaluation
│   ├── tests/                   # Tests unitaires et d'intégration
│   └── main.py                  # Point d'entrée CLI
├── docs/
│   ├── PROTOCOL_SPEC.md         # Spécification détaillée des payloads JSON-RPC
│   ├── ARCHITECTURE.md          # Architecture technique et flux de données
│   └── GETTING_STARTED.md       # Guide d'installation et de prise en main
└── README.md
```

---

## Démarrage Rapide

### 1. Lancer le Benchmark Automatisé
```bash
cd agent-debugger
pip install -r requirements.txt
python main.py --benchmark
```

### 2. Connecter l'Agent à une Scène Unity Active
```bash
python main.py --host 127.0.0.1 --port 8080 --provider heuristic
```

Pour utiliser un modèle LLM distant comme Google Gemini :
```bash
python main.py --host 127.0.0.1 --port 8080 --provider gemini --api-key YOUR_API_KEY
```

---

## Documentation Complète
- [Spécification du Protocole JSON-RPC](docs/PROTOCOL_SPEC.md)
- [Architecture Technique](docs/ARCHITECTURE.md)
- [Guide d'Installation & Prise en Main](docs/GETTING_STARTED.md)