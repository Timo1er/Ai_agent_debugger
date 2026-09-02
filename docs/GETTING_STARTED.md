# Guide de Démarrage Rapide

## 1. Prérequis
- **Unity** : Version 2021.3 LTS ou ultérieure.
- **Python** : 3.9+ avec `pip`.

---

## 2. Installation du Package Unity

1. Copiez le dossier `unity-debugger-bridge/` dans le dossier `Packages/` de votre projet Unity, ou ajoutez-le via le **Unity Package Manager** :
   - Ouvrez Unity -> `Window` -> `Package Manager`.
   - Cliquez sur le bouton `+` -> `Add package from disk...`.
   - Sélectionnez `unity-debugger-bridge/package.json`.

2. **Mise en place de la Scène** :
   - Ajoutez le préfabriqué ou le composant `SandboxManager` sur un GameObject vide de votre scène.
   - Le serveur WebSocket démarre automatiquement sur le port `8080`.
   - Vous pouvez générer un environnement sandbox 2D/3D procédural immédiat en appelant `SandboxSceneBuilder.BuildProceduralSandbox()`.

---

## 3. Lancement de l'Agent de Débogage IA (Python)

1. **Installation des dépendances** :
   ```bash
   cd agent-debugger
   pip install -r requirements.txt
   ```

2. **Lancement en mode Surveillance Temps Réel** :
   ```bash
   python main.py --host 127.0.0.1 --port 8080 --provider heuristic
   ```

3. **Utilisation avec un modèle LLM distant (ex: Gemini)** :
   ```bash
   python main.py --host 127.0.0.1 --port 8080 --provider gemini --api-key YOUR_API_KEY
   ```

---

## 4. Exécution du Banc de Test d'Évaluation (Benchmark)

Pour évaluer automatiquement l'agent contre l'ensemble des 5 scénarios du Chaos Engine :
```bash
python main.py --benchmark
```
Le banc mesure :
- **TTD (Time To Diagnose)** : Temps de détection et d'isolation de l'anomalie.
- **TTR (Time To Resolve)** : Temps total d'application du correctif.
- **Diagnostic Accuracy** : Précision du ciblage (composant et variable incriminée).
- **Post-Fix Health** : Stabilisation des métriques (FPS, mémoire, arrêt des logs d'erreur).