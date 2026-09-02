# Spécification du Protocole de Débogage & Télémétrie IA (Unity <-> Agent)

## 1. Vue d'Ensemble
La communication entre le moteur Unity et le système multi-agents repose sur une liaison bidirectionnelle WebSocket / JSON-RPC 2.0 opérant par défaut sur `ws://127.0.0.1:8080`.

Le protocole supporte :
- **Appels RPC Synchrones/Asynchrones** : Requêtes/Réponses pour inspecter, modifier et agir sur le runtime Unity.
- **Notifications Temps Réel (Push)** : Streaming continu de télémétrie, logs d'erreurs et événements de collision.

---

## 2. Format des Messages JSON-RPC 2.0

### Format de Requête
```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid-12345",
  "method": "<nom_methode>",
  "params": "<json_string_ou_object>"
}
```

### Format de Réponse Succès
```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid-12345",
  "result": { ... },
  "error": null
}
```

### Format d'Erreur
```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid-12345",
  "result": null,
  "error": {
    "code": -32603,
    "message": "Description de l'exception",
    "data": "Stack trace C#"
  }
}
```

---

## 3. Méthodes RPC Disponibles

### A. Inspection & Réflexion (`inspector.*`)

#### `inspector.getHierarchy`
Renvoie l'arborescence complète de la scène avec composants et champs publics/privés.
- **Params** : `{ "maxDepth": 4, "includeInactive": true }`
- **Result** : Liste de `GameObjectNode`.

#### `inspector.findObjects`
Recherche des objets par nom, tag ou type de composant.
- **Params** : `{ "namePattern": "Player", "tag": "Player", "typeName": "PlayerController" }`

#### `inspector.setMember`
Modifie une variable membre ou propriété via réflexion C#.
- **Params** :
```json
{
  "instanceId": 201,
  "componentTypeName": "Player3DController",
  "memberName": "moveSpeed",
  "value": "12.5"
}
```

#### `inspector.invokeMethod`
Invoque une méthode C# sur un composant au runtime.
- **Params** :
```json
{
  "instanceId": 201,
  "componentTypeName": "Player3DController",
  "methodName": "ResetState",
  "args": []
}
```

#### `inspector.setComponentActive`
Active ou désactive un composant (`Behaviour`, `Collider`, `Collider2D`).
- **Params** : `{ "instanceId": 201, "componentTypeName": "Rigidbody", "active": true }`

#### `inspector.setGameObjectActive`
Active ou désactive un `GameObject`.
- **Params** : `{ "instanceId": 201, "active": true }`

---

### B. Contrôle du Time Step (`timestep.*`)

#### `timestep.setTimeScale`
Modifie `Time.timeScale` (de `0.0` à `100.0`).
- **Params** : `{ "scale": 0.5 }`

#### `timestep.pause` / `timestep.resume`
Met le jeu en pause (`Time.timeScale = 0`) ou reprend à la vitesse précédente.

#### `timestep.stepFrames`
Avance le jeu frame par frame d'un nombre déterminé de pas puis se remet en pause.
- **Params** : `{ "frames": 1 }`

---

### C. Analyse Spatiale 2D & 3D (`spatial.*`)

#### `spatial.getEntities2D`
Renvoie les positions (`Vector2`), vélocités `Rigidbody2D`, rotation et bounding boxes de tous les objets 2D actifs.

#### `spatial.getEntities3D`
Renvoie les coordonnées 3D (`Vector3`, `Quaternion`), vélocités linéaires/angulaires `Rigidbody`, et détection de collision.

#### `spatial.raycast3D`
Effectue un lancer de rayon physique distant dans l'espace Unity.
- **Params** :
```json
{
  "originX": 0.0, "originY": 1.0, "originZ": 0.0,
  "dirX": 0.0, "dirY": 0.0, "dirZ": 1.0,
  "maxDistance": 50.0
}
```

---

### D. Exécution Dynamique & Hot-Patching (`eval.*`)

#### `eval.executeCode`
Exécute un snippet C# dynamique pour corriger un bug en direct.
- **Params** :
```json
{
  "code": "SET Player3D.Player3DController.targetTransform = Ground3D"
}
```
- **Result** :
```json
{
  "success": true,
  "returnValue": "Successfully set ...",
  "logs": "[DEBUG] Code evaluated successfully.",
  "executionTimeMs": 1.2
}
```

---

### E. Moteur de Chaos (`chaos.*`)

#### `chaos.inject`
Injecte un scénario de bug dans la scène sandbox.
- **Params** : `{ "scenarioName": "null_reference_cascade", "parametersJson": "{}" }`

#### `chaos.reset`
Réinitialise tous les scénarios de chaos à leur état nominal.

#### `chaos.getStatus`
Renvoie le statut actif du moteur de chaos et l'état des scénarios.

---

## 4. Notifications Push de Télémétrie

### Snapshot Périodique (`telemetry.snapshot`)
Diffusé automatiquement à intervalle régulier (5 Hz - 30 Hz).
```json
{
  "jsonrpc": "2.0",
  "method": "telemetry.snapshot",
  "params": {
    "timestamp": "2026-08-31T12:00:00Z",
    "frameCount": 1542,
    "timeSinceStartup": 45.2,
    "timeScale": 1.0,
    "metrics": {
      "fps": 59.8,
      "frameTimeMs": 16.7,
      "gcMemoryBytes": 18450210,
      "totalAllocatedMemoryBytes": 52140000,
      "activeGameObjectsCount": 24,
      "totalComponentsCount": 78,
      "drawCallsCount": 12
    },
    "recentLogs": [
      {
        "timestamp": "2026-08-31T12:00:00Z",
        "frame": 1540,
        "type": "Error",
        "message": "NullReferenceException at PlayerController.Update()",
        "stackTrace": "at PlayerController.UpdateMovement() ..."
      }
    ],
    "entities2D": [ ... ],
    "entities3D": [ ... ],
    "recentCollisions": [ ... ],
    "activeChaosScenario": "null_reference_cascade"
  }
}
```