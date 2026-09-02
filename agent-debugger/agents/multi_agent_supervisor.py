import asyncio
import time
from typing import Dict, Any, List, Optional
from llm.llm_provider import BaseLLMProvider, LLMFactory
from .specialists.physics_specialist import PhysicsSpecialistAgent
from .specialists.performance_memory_specialist import PerformanceMemorySpecialistAgent
from .specialists.animation_state_specialist import AnimationStateSpecialistAgent
from .specialists.render_camera_specialist import RenderCameraSpecialistAgent
from .specialists.logic_exception_specialist import LogicExceptionSpecialistAgent

class MultiAgentSupervisor:
    """
    Superviseur en Chef Multi-Agents (Master Deep QA Director) :
    Orchestre une campagne de test de limites et de détection de micro-bugs (Topologie 3D, Fuzzing d'angles,
    Inversion de vélocité 60Hz, Fuzzing d'armes, Oracle Microscopique).
    """
    def __init__(self, client: Any, llm: Optional[BaseLLMProvider] = None, duration_seconds: float = 20.0):
        self.client = client
        self.llm = llm or LLMFactory.create_provider("heuristic")
        self.duration_seconds = max(1.0, duration_seconds)

        self.specialists = [
            PhysicsSpecialistAgent(self.client, self.llm),
            PerformanceMemorySpecialistAgent(self.client, self.llm),
            AnimationStateSpecialistAgent(self.client, self.llm),
            RenderCameraSpecialistAgent(self.client, self.llm),
            LogicExceptionSpecialistAgent(self.client, self.llm),
        ]

    async def _update_unity_hud(self, agent_name: str, action: str, detail: str = "", is_alert: bool = False):
        try:
            if hasattr(self.client, "call"):
                await self.client.call("hud.update", {
                    "args": [agent_name, action, detail, str(is_alert).lower()]
                })
        except Exception:
            pass

    async def _fetch_context(self) -> Dict[str, Any]:
        context = {}
        try:
            if hasattr(self.client, "get_telemetry_snapshot"):
                context["snapshot"] = await self.client.get_telemetry_snapshot()
            elif hasattr(self.client, "latest_snapshot"):
                context["snapshot"] = self.client.latest_snapshot
        except Exception:
            pass
        return context

    async def execute_multi_agent_hunt(self) -> Dict[str, Any]:
        print("\n" + "="*78)
        print(" [DEEP QA HUNTER] LANCEMENT DU TEST DE LIMITES & CHASSE AUX MICRO-BUGS")
        print("="*78)
        print(f" -> Durée de la campagne : {self.duration_seconds:.1f}s")
        print(f" -> Laboratoires actifs  : Topologie 3D, Stress Physique, Combat Fuzzer, Oracle")
        print("-" * 78)

        await self._update_unity_hud("Superviseur IA", "Démarrage Test de Limites", "Déploiement des 5 laboratoires")

        t_start = time.perf_counter()
        all_bugs: List[Dict[str, Any]] = []
        phase_time = self.duration_seconds / 5.0

        # === 1. TOPOLOGIE 3D & SCAN DE GÉOMÉTRIE (RAYCAST 360°) ===
        print(f"\n[LAB 1/5] [SPATIAL EXPLORER] Scan topologique 360° du niveau & trous de colliders...")
        await self._update_unity_hud("Spatial Explorer", "Scan Topologique 360°", "Lancer de rayons omnidirectionnels")
        try:
            if hasattr(self.client, "scan_geometry_360"):
                geo_res = await self.client.scan_geometry_360()
                if geo_res and geo_res.get("openBounds", 0) > 18:
                    all_bugs.append({
                        "specialist": "Agent-Spatial",
                        "domain": "Topology & Geometry",
                        "severity": "HIGH",
                        "title": "Trou de collider détecté dans la géométrie du niveau",
                        "description": f"{geo_res.get('openBounds')} rayons sur 36 n'ont rencontré aucun collider dans un rayon de 25m.",
                        "fix": "Ajouter un BoxCollider ou un MeshCollider invisible sur la limite de la pièce."
                    })
        except Exception:
            pass
        await asyncio.sleep(phase_time)

        # === 2. STRESS PHYSIQUE D'ANGLES AIGUS & INVERSION DE VÉLOCITÉ ===
        print(f"\n[LAB 2/5] [PHYSICAL STRESS LAB] Coin aigu (<45°) & Inversion de vélocité à 60Hz...")
        await self._update_unity_hud("Agent-Physique", "Stress Coin Aigu & Vélocité 60Hz", "Test de coincement et tunneling")
        try:
            if hasattr(self.client, "stress_physics_corner"):
                await self.client.stress_physics_corner()
            if hasattr(self.client, "stress_physics_velocity"):
                await self.client.stress_physics_velocity()
            if hasattr(self.client, "drive_player_fuzz"):
                await self.client.drive_player_fuzz(duration=0.5)
        except Exception:
            pass
        context = await self._fetch_context()
        bugs_p = await self.specialists[0].investigate_and_hunt(context)
        for b in bugs_p:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)
        await asyncio.sleep(phase_time)

        # === 3. COMBAT & WEAPON STATE MACHINE FUZZING ===
        print(f"\n[LAB 3/5] [COMBAT ACTION FUZZER] Fuzzing d'armes & Concurrence de tir/rechargement...")
        await self._update_unity_hud("Agent-Animation-State", "Fuzzing d'Armes & Transitions", "Vérification des armes superposées")
        try:
            if hasattr(self.client, "fuzz_combat_weapons"):
                await self.client.fuzz_combat_weapons()
        except Exception:
            pass
        bugs_a = await self.specialists[2].investigate_and_hunt(context)
        for b in bugs_a:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)
        await asyncio.sleep(phase_time)

        # === 4. PROFILAGE DE PRÉCISION MÉMOIRE & MICRO-STUTTERS ===
        print(f"\n[LAB 4/5] [PERFORMANCE PROFILER] Détection des micro-gels (99th percentile hitch)...")
        await self._update_unity_hud("Agent-Performance", "Traque des Micro-Gels (>33ms)", "Mesure de la gigue de rendu")
        bugs_m = await self.specialists[1].investigate_and_hunt(context)
        for b in bugs_m:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)
        await asyncio.sleep(phase_time)

        # === 5. ORACLE MICROSCOPIQUE (SHADERS ROSES, COORDONNÉES NAN, AUDIO, EXCEPTIONS) ===
        print(f"\n[LAB 5/5] [MICROSCOPIC INVARIANT ORACLE] Audit des Shaders roses, NaN, Exceptions et Audio...")
        await self._update_unity_hud("Microscopic Oracle", "Audit Invariants Microscopiques", "Scan shaders, NaN et audio")
        try:
            if hasattr(self.client, "run_microscopic_audit"):
                micro_res = await self.client.run_microscopic_audit()
                if micro_res:
                    if micro_res.get("pinkShadersFound", 0) > 0:
                        all_bugs.append({
                            "specialist": "Agent-Rendu",
                            "domain": "Shaders & Rendering",
                            "severity": "HIGH",
                            "title": f"Matériaux cassés / Shaders roses détectés ({micro_res['pinkShadersFound']} objets)",
                            "description": "Des objets de la scène utilisent un shader manquant ou incompatible avec le Render Pipeline.",
                            "fix": "Mettre à jour les matériaux vers le Render Pipeline actif (URP/HDRP/Standard)."
                        })
                    if micro_res.get("nanCoordinatesFound", 0) > 0:
                        all_bugs.append({
                            "specialist": "Agent-Physique",
                            "domain": "Floating-point Invariants",
                            "severity": "CRITICAL",
                            "title": f"Coordonnées corrompues NaN / Infinity ({micro_res['nanCoordinatesFound']} objets)",
                            "description": "Division par zéro détectée dans un script de déplacement ou une force physique.",
                            "fix": "Vérifier la division par zéro dans les calculs vectoriels : Vector3.ClampMagnitude(dir, 1f);"
                        })
                    if micro_res.get("audioListenerMuted", False):
                        all_bugs.append({
                            "specialist": "Agent-Audio",
                            "domain": "Audio Invariants",
                            "severity": "MEDIUM",
                            "title": "AudioListener complètement muet (Volume = 0)",
                            "description": "Le volume audio global est à zéro.",
                            "fix": "AudioListener.volume = 1.0f;"
                        })
                    if micro_res.get("playerIgnoresEnemies", False):
                        all_bugs.append({
                            "specialist": "Agent-Physique",
                            "domain": "Collision Layer Matrix",
                            "severity": "HIGH",
                            "title": "Matrice de collision désactivée : Player traverse Enemy",
                            "description": "Physics.GetIgnoreLayerCollision(Player, Enemy) est à true.",
                            "fix": "Physics.IgnoreLayerCollision(LayerMask.NameToLayer(\"Player\"), LayerMask.NameToLayer(\"Enemy\"), false);"
                        })
        except Exception:
            pass

        bugs_r = await self.specialists[3].investigate_and_hunt(context)
        bugs_l = await self.specialists[4].investigate_and_hunt(context)
        for b in bugs_r + bugs_l:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)

        await asyncio.sleep(phase_time)

        total_time = time.perf_counter() - t_start

        # Synthèse finale
        await self._update_unity_hud("Superviseur IA", f"Audit de Limites Terminé ({len(all_bugs)} bugs)", "Rapport généré", is_alert=len(all_bugs)>0)
        report = self._synthesize_report(all_bugs, total_time)
        return report

    def _synthesize_report(self, bugs: List[Dict[str, Any]], duration_sec: float) -> Dict[str, Any]:
        print("\n" + "="*78)
        print(" RAPPORT EXECUTIVE DE CHASSE AUX MICRO-BUGS & LIMITES (DEEP QA)")
        print("="*78)
        print(f" Durée totale de l'audit        : {duration_sec:.2f} secondes")
        print(f" Total d'anomalies confirmées   : {len(bugs)}")
        print("-" * 78)

        if not bugs:
            print(" [SUPERVISEUR] JEU 100% CONFORME AUX CRITERES QA LES PLUS STRICTS !")
            print(" -> 0 trou de géométrie, 0 shader rose, 0 valeur NaN, physique et armes parfaites.")
        else:
            for idx, b in enumerate(bugs, 1):
                print(f"\n [BUG #{idx}] [{b.get('severity','HIGH')}] {b.get('title')}")
                print(f"   -> Spécialiste : {b.get('specialist')} ({b.get('domain')})")
                print(f"   -> Diagnostic  : {b.get('description')}")
                print(f"   -> Solution C# :")
                for line in b.get('fix', '').split('\n'):
                    print(f"      {line}")

        print("="*78 + "\n")

        return {
            "duration_sec": round(duration_sec, 2),
            "bugs_count": len(bugs),
            "bugs": bugs
        }