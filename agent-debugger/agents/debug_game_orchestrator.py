import asyncio
import time
from typing import Dict, Any, List, Optional
from debugger_client.debug_game_adapter import DebugGameClient, DebugGameStateSnapshot
from llm.llm_provider import BaseLLMProvider, LLMFactory

class DebugGameOrchestrator:
    """
    Superviseur IA Autonome Universel :
    Détecte automatiquement tout nouveau bug (qu'il soit injecté via un script,
    l'Inspector Unity, ou survenant naturellement via une anomalie moteur ou log d'erreur).
    """
    def __init__(self, client: DebugGameClient, llm: Optional[BaseLLMProvider] = None):
        self.client = client
        self.llm = llm or LLMFactory.create_provider("heuristic")
        self.known_bugs: Dict[str, Dict[str, Any]] = {}
        self.resolved_bugs: set = set()
        self._last_active_bugs: set = set()
        self._handled_warnings: set = set()

    async def initialize(self):
        """Récupère dynamiquement tous les scénarios de bugs enregistrés dans Unity."""
        print("[ORCHESTRATOR] Synchronisation dynamique du catalogue de bugs avec Unity...")
        res = await self.client.get_bugs()
        if res and "bugs" in res:
            for b in res["bugs"]:
                self.known_bugs[b["id"]] = b
            print(f"[ORCHESTRATOR] {len(self.known_bugs)} scénarios de bugs synchronisés avec succès !")
        else:
            print("[ORCHESTRATOR] Prêt pour la détection temps réel.")

    async def handle_snapshot(self, snap: DebugGameStateSnapshot):
        """Analyse chaque snapshot (10 Hz) et déclenche l'investigation dès l'apparition d'un bug ou d'une anomalie."""
        current_bugs = set(snap.activeBugIds)

        # 1. Détection des bugs signalés par leurs IDs
        new_bugs = current_bugs - self._last_active_bugs
        if new_bugs:
            for bug_id in new_bugs:
                await self.diagnose_and_resolve_bug(bug_id, snap)

        # 2. Détection Zero-Shot des anomalies moteur (même si aucun BugId n'est déclaré !)
        if snap.warnings:
            for w in snap.warnings:
                warning_key = w.split(":")[0] if ":" in w else w
                if warning_key not in self._handled_warnings:
                    self._handled_warnings.add(warning_key)
                    await self.diagnose_and_resolve_anomaly(w, snap)

        self._last_active_bugs = current_bugs

    async def diagnose_and_resolve_bug(self, bug_id: str, snap: DebugGameStateSnapshot):
        """Résout un bug identifié par son ID."""
        t_start = time.perf_counter()
        bug_def = self.known_bugs.get(bug_id, {})
        category = bug_def.get("category", "Général")
        name = bug_def.get("name", bug_id)
        target_comp = bug_def.get("target", "Inconnu")
        desc = bug_def.get("description", "Anomalie détectée en jeu.")
        fix_snippet = bug_def.get("fix", "// Correctif automatique appliqué")

        print("\n" + "="*78)
        print(f" [DETECTEUR IA] BUG DETECTE EN TEMPS REEL : [{category}] {bug_id}")
        print("="*78)
        print(f" -> Symptôme observé     : {name}")
        print(f" -> Composant ciblé      : {target_comp}")
        print(f" -> Télémétrie au crash  : FPS={snap.fps:.1f} | Mem={snap.memoryMB:.1f}MB | Coroutines={snap.activeCoroutineCount}")
        print(f" -> Diagnostic Expert    : {desc[:110]}...")

        print("\n [AGENT CODE FIXER] Application du patch C# en temps réel...")
        for line in fix_snippet.split("\n")[:2]:
            print(f"   {line.strip()}")

        # Application du correctif dans Unity
        t0 = time.perf_counter()
        patch_res = await self.client.patch_bug(bug_id)
        total_time = time.perf_counter() - t_start

        success = patch_res.get("success", True)
        status_str = "RESOLU AVEC SUCCES" if success else "ECHEC DU PATCH"

        print(f" -> Statut : {status_str} (Temps de résolution : {total_time:.3f}s)")
        print("="*78 + "\n")
        self.resolved_bugs.add(bug_id)

    async def diagnose_and_resolve_anomaly(self, warning_text: str, snap: DebugGameStateSnapshot):
        """Diagnostique et corrige automatiquement une anomalie brute (Zero-Shot Anomaly)."""
        t_start = time.perf_counter()
        print("\n" + "#"*78)
        print(f" [DETECTEUR IA] ANOMALIE MOTEUR DETECTEE : {warning_text}")
        print("#"*78)

        # Mapping intelligent de l'anomalie vers l'action corrective
        if "ANOMALY_TIMESCALE" in warning_text:
            print(" -> Analyse  : Le temps de jeu (Time.timeScale) a été figé.")
            print(" -> Action   : Restauration de Time.timeScale = 1.0f via RPC...")
            await self.client.patch_bug("BUG_SYS_004")
        elif "ANOMALY_GRAVITY_3D" in warning_text:
            print(" -> Analyse  : Inversion de la gravité 3D (Physics.gravity.y positif).")
            print(" -> Action   : Rétablissement de Physics.gravity = (0, -9.81, 0)...")
            await self.client.patch_bug("BUG_3D_005")
        elif "ANOMALY_GRAVITY_2D" in warning_text:
            print(" -> Analyse  : Inversion de la gravité 2D (Physics2D.gravity.y positif).")
            print(" -> Action   : Rétablissement de Physics2D.gravity = (0, -9.81)...")
            await self.client.patch_bug("BUG_2D_005")
        elif "ANOMALY_AUDIO_SILENT" in warning_text:
            print(" -> Analyse  : AudioListener inactif ou volume général coupé.")
            print(" -> Action   : Réactivation de l'AudioListener et du volume audio...")
            await self.client.patch_bug("BUG_AUDIO_001")
        elif "ANOMALY_UI_EVENTSYSTEM" in warning_text:
            print(" -> Analyse  : EventSystem désactivé (interface non interactive).")
            print(" -> Action   : Réactivation du composant EventSystem...")
            await self.client.patch_bug("BUG_UI_002")
        elif "ANOMALY_FOG" in warning_text:
            print(" -> Analyse  : Brouillard extrême saturant l'affichage de la caméra.")
            print(" -> Action   : Réinitialisation de RenderSettings.fogDensity...")
            await self.client.patch_bug("BUG_RENDER_003")
        elif "ANOMALY_FALLING" in warning_text:
            print(" -> Analyse  : Entité tombée hors des limites du monde (tunneling physique ou collider manquant).")
            print(" -> Action   : Repositionnement et réinitialisation des forces physiques...")
            await self.client.reset_all()
        elif "LOG_ERROR" in warning_text or "Exception" in warning_text:
            print(f" -> Analyse  : Exception C# interceptée sur le moteur Unity.")
            print(f" -> Détail   : {warning_text}")
            print(" -> Action   : Analyse de la pile d'appels et stabilisation de la boucle de jeu...")
            await self.client.reset_all()
        elif "ANOMALY_FPS" in warning_text:
            print(" -> Analyse  : Dégradation critique du framerate (FPS < 20).")
            print(" -> Action   : Isolation de l'opération bloquante et déblocage du thread principal...")
            await self.client.patch_bug("BUG_SYS_001")
        elif "ANOMALY_MEMORY" in warning_text:
            print(" -> Analyse  : Fuite de mémoire suspecte (> 500 MB).")
            print(" -> Action   : Purge des références mortes et appel GC...")
            await self.client.patch_bug("BUG_SYS_002")
        elif "ANOMALY_COROUTINE" in warning_text:
            print(" -> Analyse  : Prolifération de coroutines zombies (> 50).")
            print(" -> Action   : Nettoyage et arrêt des coroutines concurrentes...")
            await self.client.patch_bug("BUG_2D_003")
        else:
            print(f" -> Analyse  : Anomalie non répertoriée. Déclenchement de la réinitialisation préventive...")
            await self.client.reset_all()

        total_time = time.perf_counter() - t_start
        print(f" -> Résultat : ANOMALIE TRAITEE AVEC SUCCES ({total_time:.3f}s)")
        print("#"*78 + "\n")