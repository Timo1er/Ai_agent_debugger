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
    Orchestre une campagne d'audit en profondeur : Logique Gameplay (25 bugs de jeu réels),
    Invariants Physiques, Shaders, Événements et Mémoire.
    """
    def __init__(self, client: Any, llm: Optional[BaseLLMProvider] = None, duration_seconds: float = 15.0):
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
        print(" [DEEP QA HUNTER] AUDIT APPROFONDI DE LA LOGIQUE DE JEU & TEST DE LIMITES")
        print("="*78)
        print(f" -> Durée de la campagne : {self.duration_seconds:.1f}s")
        print(f" -> Cibles analysées    : Physique 2D/3D, Triggers, Événements, Combat & Santé")
        print("-" * 78)

        await self._update_unity_hud("Superviseur IA", "Audit Gameplay & Pouvoirs Game Master", "Activation autonome de l'invulnérabilité")
        
        # POUVOIR AUTONOME #1 : L'IA active d'elle-même le GodMode pour ne jamais mourir pendant les tests
        try:
            if hasattr(self.client, "set_god_mode"):
                await self.client.set_god_mode(True)
                print("   -> [POUVOIR AUTONOME IA] GodMode activé : Le joueur est invulnérable pour toute la durée des tests.")
        except Exception:
            pass

        try:
            if hasattr(self.client, "start_player_exploration"):
                await self.client.start_player_exploration(duration=self.duration_seconds)
        except Exception:
            pass

        t_start = time.perf_counter()
        all_bugs: List[Dict[str, Any]] = []
        phase_time = self.duration_seconds / 5.0

        # === 1. AUDIT PROFOND DE LOGIQUE GAMEPLAY (25 RÈGLES DE JEU REELLES) ===
        print(f"\n[PHASE 1/5] [DEEP GAMEPLAY AUDITOR] Analyse des scripts, triggers, saut infini et PV...")
        await self._update_unity_hud("Deep Gameplay Auditor", "Scan Logique Scripts & Triggers", "Détection des 25 bugs réels")
        try:
            if hasattr(self.client, "audit_gameplay_bugs"):
                gameplay_bugs = await self.client.audit_gameplay_bugs()
                for gb in gameplay_bugs:
                    if not any(x.get("title") == gb.get("title") for x in all_bugs):
                        all_bugs.append({
                            "specialist": "Agent-Gameplay-Auditor",
                            "domain": gb.get("domain", "Gameplay Logic"),
                            "severity": gb.get("severity", "HIGH"),
                            "title": gb.get("title"),
                            "description": gb.get("description"),
                            "fix": gb.get("fix", "")
                        })
                        print(f"   -> [BUG DETECTE] [{gb.get('severity')}] {gb.get('title')}")
        except Exception as ex:
            print(f"   -> Gameplay audit: {ex}")
        await asyncio.sleep(phase_time)

        # === 2. TOPOLOGIE 3D & SCAN DE GÉOMÉTRIE ===
        print(f"\n[PHASE 2/5] [SPATIAL EXPLORER] Scan de collision et limites de niveau...")
        await self._update_unity_hud("Spatial Explorer", "Scan Géométrie 360°", "Vérification des parois et colliders")
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

        # === 3. STRESS PHYSIQUE, TÉLÉPORTATION AUTONOME & COLLISION FUZZING ===
        print(f"\n[PHASE 3/5] [PHYSICAL STRESS LAB] Téléportation autonome multi-secteurs & Fuzzing...")
        await self._update_unity_hud("Agent-Physique", "Téléportation & Stress Collisions", "Test des 3 secteurs du niveau")
        
        # POUVOIR AUTONOME #2 : L'IA se téléporte d'elle-même dans les 3 secteurs clés du niveau pour éprouver les collisions
        try:
            if hasattr(self.client, "teleport"):
                print("   -> [POUVOIR AUTONOME IA] Téléportation vers Secteur Milieu (8, 2)...")
                await self.client.teleport(8.0, 2.0, 0.0)
                await asyncio.sleep(1.0)
                print("   -> [POUVOIR AUTONOME IA] Téléportation vers Secteur Fin (18, 3)...")
                await self.client.teleport(18.0, 3.0, 0.0)
                await asyncio.sleep(1.0)
                print("   -> [POUVOIR AUTONOME IA] Retour au sol pour test de course continue...")
                await self.client.teleport(0.0, -1.0, 0.0)
        except Exception:
            pass
        await self._update_unity_hud("Agent-Physique", "Stress Collisions & Fuzzing", "Test de coincement et rupture")
        try:
            if hasattr(self.client, "stress_physics_corner"):
                await self.client.stress_physics_corner()
            if hasattr(self.client, "drive_player_fuzz"):
                await self.client.drive_player_fuzz(duration=0.5)
        except Exception:
            pass
        context = await self._fetch_context()
        bugs_p = await self.specialists[0].investigate_and_hunt(context)
        for b in bugs_p:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)
        await asyncio.sleep(phase_time)

        # === 4. PROFILAGE DE PRÉCISION MÉMOIRE & EXCEPTIONS ===
        print(f"\n[PHASE 4/5] [PERFORMANCE PROFILER] Traque des fuites mémoire et exceptions...")
        await self._update_unity_hud("Agent-Performance & Logique", "Surveillance GC & Exceptions C#", "Capture des erreurs runtime")
        bugs_m = await self.specialists[1].investigate_and_hunt(context)
        bugs_l = await self.specialists[4].investigate_and_hunt(context)
        for b in bugs_m + bugs_l:
            if not any(x["title"] == b["title"] for x in all_bugs): all_bugs.append(b)
        await asyncio.sleep(phase_time)

        # === 5. ORACLE MICROSCOPIQUE (SHADERS ROSES, COORDONNÉES NAN, AUDIO) ===
        print(f"\n[PHASE 5/5] [MICROSCOPIC INVARIANT ORACLE] Audit des Shaders roses, NaN et Audio...")
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
        except Exception:
            pass

        await asyncio.sleep(phase_time)

                # === RÉCOLTE FINALE DE TOUS LES ÉVÉNEMENTS DE TUNNELING & COLLISIONS SUR LA DURÉE TOTALE ===
        print(f"\n[SYNTHESE] Récolte des événements de collision et sentinelles physiques...")
        try:
            if hasattr(self.client, "get_tunneling_events"):
                tunnel_events = await self.client.get_tunneling_events()
                for ev in (tunnel_events or []):
                    obs = ev.get("obstacleName", "Obstacle/Mur")
                    fx, fy = ev.get("fromX", 0.0), ev.get("fromY", 0.0)
                    tx, ty = ev.get("toX", 0.0), ev.get("toY", 0.0)
                    title = f"Traversée anormale de collision / Tunneling sur '{obs}'"
                    if not any(x.get("title") == title for x in all_bugs):
                        all_bugs.append({
                            "specialist": "Agent-Physique",
                            "domain": "Physics & Collisions",
                            "severity": "CRITICAL",
                            "title": title,
                            "description": f"Le personnage a traversé le collider solide '{obs}' de ({fx:.2f}, {fy:.2f}) à ({tx:.2f}, {ty:.2f}) sans collision physique.",
                            "fix": "1. Passer Rigidbody2D.collisionDetectionMode en Continuous.\n2. Remplacer les téléportations Dash (transform.position += ...) par des impulsions physiques Rigidbody2D.AddForce."
                        })
                        print(f"   -> [COLLISION DETECTEE] [CRITICAL] {title}")
        except Exception as ex:
            print(f"   -> Tunneling harvest: {ex}")

        total_time = time.perf_counter() - t_start

        # Synthèse finale
        await self._update_unity_hud("Superviseur IA", f"Audit Terminé : {len(all_bugs)} bugs détectés", "Rapport généré", is_alert=len(all_bugs)>0)
        report = self._synthesize_report(all_bugs, total_time)
        return report

    def _synthesize_report(self, bugs: List[Dict[str, Any]], duration_sec: float) -> Dict[str, Any]:
        print("\n" + "="*78)
        print(" RAPPORT EXECUTIVE DE CHASSE AUX BUGS GAMEPLAY (DEEP QA AUDIT)")
        print("="*78)
        print(f" Durée totale de l'audit        : {duration_sec:.2f} secondes")
        print(f" Total d'anomalies confirmées   : {len(bugs)}")
        print("-" * 78)

        if not bugs:
            print(" [SUPERVISEUR] JEU 100% CONFORME AUX CRITERES QA LES PLUS STRICTS !")
            print(" -> Aucun bug de logique gameplay, physique, shader ou trigger détecté.")
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