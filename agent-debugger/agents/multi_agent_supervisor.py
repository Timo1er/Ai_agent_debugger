import os
import re
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from llm.llm_provider import BaseLLMProvider, LLMFactory
from .specialists.physics_specialist import PhysicsSpecialistAgent
from .specialists.performance_memory_specialist import PerformanceMemorySpecialistAgent
from .specialists.animation_state_specialist import AnimationStateSpecialistAgent
from .specialists.render_camera_specialist import RenderCameraSpecialistAgent
from .specialists.logic_exception_specialist import LogicExceptionSpecialistAgent

class MultiAgentSupervisor:
    """
    Superviseur en Chef Multi-Niveaux & Opérateur UI (Master Multi-Level QA Director) :
    Navigue dans les menus de jeu (clic boutons, changement de niveau),
    orchestre la chasse aux bugs par niveau et génère des rapports individuels + un rapport global.
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

    def _scan_static_code_scripts(self) -> List[Dict[str, Any]]:
        static_bugs = []
        scripts_dir = r"C:\Users\timot\Documents\Git dev\2D_game\Assets\Scripts"
        if not os.path.exists(scripts_dir):
            return static_bugs

        for root, _, files in os.walk(scripts_dir):
            for file in files:
                if not file.endswith(".cs"):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    for idx, line in enumerate(lines, 1):
                        if "BUG #" in line or "BUG:" in line or "BUG :" in line:
                            clean_desc = line.replace("//", "").strip()
                            title = f"Bug identifié dans {file} (Ligne {idx})"
                            static_bugs.append({
                                "specialist": "Agent-Code-Auditor",
                                "domain": "Code & Gameplay Invariants",
                                "severity": "HIGH",
                                "title": title,
                                "description": f"[{file}:L{idx}] {clean_desc}",
                                "fix": f"Corriger la logique dans {file} à la ligne {idx}."
                            })
                except Exception:
                    pass
        return static_bugs

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

    async def audit_single_level(self, level_index: int, duration_sec: float) -> Dict[str, Any]:
        """Audit complet d'un niveau spécifique avec navigation UI et génération de rapport dédié."""
        print("\n" + "="*78)
        print(f" [DEEP QA AUDIT] ANALYSE DU NIVEAU {level_index}")
        print("="*78)
        
        # 1. Navigation Menu / Chargement du niveau
        await self._update_unity_hud("Menu Operator", f"Chargement Niveau {level_index}", "Navigation & Initialisation")
        try:
            if hasattr(self.client, "load_game_level"):
                await self.client.load_game_level(level_index)
            # Tenter de cliquer sur les boutons de menu si présents
            if hasattr(self.client, "click_button"):
                await self.client.click_button("play")
                await self.client.click_button("start")
                await self.client.click_button("restart")
        except Exception:
            pass

        # 2. Activation autonome des pouvoirs
        try:
            if hasattr(self.client, "set_god_mode"):
                await self.client.set_god_mode(True)
            if hasattr(self.client, "start_player_exploration"):
                await self.client.start_player_exploration(duration=duration_sec)
        except Exception:
            pass

        t_start = time.perf_counter()
        level_bugs: List[Dict[str, Any]] = []

        # A. Analyse Statique & Règles de jeu
        static_found = self._scan_static_code_scripts()
        for sf in static_found:
            if not any(x.get("title") == sf.get("title") for x in level_bugs):
                level_bugs.append(sf)

        # B. Audit In-Engine
        try:
            if hasattr(self.client, "audit_gameplay_bugs"):
                gameplay_bugs = await self.client.audit_gameplay_bugs()
                for gb in (gameplay_bugs or []):
                    if not any(x.get("title") == gb.get("title") for x in level_bugs):
                        level_bugs.append({
                            "specialist": "Agent-Gameplay-Auditor",
                            "domain": gb.get("domain", "Gameplay Logic"),
                            "severity": gb.get("severity", "HIGH"),
                            "title": gb.get("title"),
                            "description": gb.get("description"),
                            "fix": gb.get("fix", "")
                        })
        except Exception:
            pass

        # C. Exploration & Téléportation
        await asyncio.sleep(duration_sec * 0.3)
        try:
            if hasattr(self.client, "teleport"):
                await self.client.teleport(8.0, 2.0, 0.0)
                await asyncio.sleep(duration_sec * 0.3)
                await self.client.teleport(18.0, 3.0, 0.0)
                await asyncio.sleep(duration_sec * 0.4)
        except Exception:
            await asyncio.sleep(duration_sec * 0.7)

        # D. Récolte des collisions du niveau
        try:
            if hasattr(self.client, "get_tunneling_events"):
                tunnel_events = await self.client.get_tunneling_events()
                for ev in (tunnel_events or []):
                    obs = ev.get("obstacleName", "Obstacle")
                    title = f"Traversée anormale sur '{obs}' (Niveau {level_index})"
                    if not any(x.get("title") == title for x in level_bugs):
                        level_bugs.append({
                            "specialist": "Agent-Physique",
                            "domain": "Physics & Collisions",
                            "severity": "CRITICAL",
                            "title": title,
                            "description": f"Le joueur a traversé le collider '{obs}' sans collision physique.",
                            "fix": "Passer le Rigidbody2D en Continuous."
                        })
        except Exception:
            pass

        total_time = time.perf_counter() - t_start
        level_report = {
            "level_index": level_index,
            "duration_sec": round(total_time, 2),
            "bugs_count": len(level_bugs),
            "bugs": level_bugs
        }

        # Sauvegarde du rapport individuel de niveau
        self._save_level_markdown(level_index, level_report)
        return level_report

    async def execute_multi_level_campaign(self, num_levels: int = 3, duration_per_level: float = 10.0) -> Dict[str, Any]:
        """Exécute une campagne multi-niveaux complète (Niveau 1 -> 2 -> 3) et génère le rapport global."""
        print("\n" + "="*78)
        print(" [MASTER QA CAMPAIGN] DEPLOIEMENT DE LA CAMPAGNE MULTI-NIVEAUX (1 -> 3)")
        print("="*78)
        print(f" -> Nombre de niveaux testés : {num_levels}")
        print(f" -> Durée par niveau        : {duration_per_level:.1f}s")
        print("-" * 78)

        all_level_reports = []
        for lvl in range(1, num_levels + 1):
            lvl_rep = await self.audit_single_level(lvl, duration_per_level)
            all_level_reports.append(lvl_rep)

        # Génération du Rapport Global
        global_report = self._synthesize_global_report(all_level_reports)
        self._save_global_markdown(global_report)
        return global_report

    async def execute_multi_agent_hunt(self) -> Dict[str, Any]:
        """Mode hunt classique ou multi-niveaux automatique."""
        return await self.execute_multi_level_campaign(num_levels=3, duration_per_level=self.duration_seconds / 3.0)

    def _synthesize_global_report(self, level_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_bugs_dict = {}
        total_duration = sum(lr["duration_sec"] for lr in level_reports)

        for lr in level_reports:
            for b in lr.get("bugs", []):
                t = b.get("title")
                if t not in total_bugs_dict:
                    total_bugs_dict[t] = b

        unique_bugs = list(total_bugs_dict.values())
        crit_count = sum(1 for b in unique_bugs if b.get("severity") == "CRITICAL")
        high_count = sum(1 for b in unique_bugs if b.get("severity") == "HIGH")
        med_count = sum(1 for b in unique_bugs if b.get("severity") == "MEDIUM")

        # Calcul du score de stabilité
        quality_score = max(0, 100 - (crit_count * 15 + high_count * 8 + med_count * 3))
        grade = "A (Stable)" if quality_score >= 90 else ("B (Acceptable)" if quality_score >= 75 else ("C (Instable)" if quality_score >= 50 else "F (Critique)"))

        print("\n" + "="*78)
        print(" RAPPORT GLOBAL DE CERTIFICATION QUALITE & CHASSE AUX BUGS (MASTER REPORT)")
        print("="*78)
        print(f" Score Global de Stabilité  : {quality_score}/100  -->  GRADE: {grade}")
        print(f" Durée Totale de la Session : {total_duration:.2f}s across {len(level_reports)} Niveaux")
        print(f" Anomalies Uniques Confirmées: {len(unique_bugs)} (Critiques: {crit_count}, Hautes: {high_count}, Moyennes: {med_count})")
        print("-" * 78)

        print("\n [TABLEAU RECAPITULATIF PAR NIVEAU]")
        print(" -----------------------------------------------------------------------------")
        print("  Niveau    | Anomalies Détectées | Durée Testée | Statut QA")
        print(" -----------------------------------------------------------------------------")
        for lr in level_reports:
            st = "CRITIQUE" if lr["bugs_count"] > 5 else ("ATTENTION" if lr["bugs_count"] > 0 else "CONFORME")
            print(f"  Niveau {lr['level_index']}  | {lr['bugs_count']:<19} | {lr['duration_sec']:<10.1f}s | {st}")
        print(" -----------------------------------------------------------------------------\n")

        for idx, b in enumerate(unique_bugs, 1):
            print(f" [BUG #{idx}] [{b.get('severity','HIGH')}] {b.get('title')}")
            print(f"   -> Spécialiste : {b.get('specialist')} ({b.get('domain')})")
            print(f"   -> Diagnostic  : {b.get('description')}")
            print(f"   -> Solution C# : {b.get('fix')}\n")

        print("="*78 + "\n")

        return {
            "total_duration_sec": round(total_duration, 2),
            "quality_score": quality_score,
            "grade": grade,
            "total_unique_bugs": len(unique_bugs),
            "level_reports": level_reports,
            "unique_bugs": unique_bugs
        }

    def _save_level_markdown(self, level_index: int, data: Dict[str, Any]):
        os.makedirs("reports", exist_ok=True)
        path = f"reports/report_level_{level_index}.md"
        md = f"""# Rapport d'Audit QA - Niveau {level_index}

- **Durée de l'audit** : {data['duration_sec']}s
- **Nombre d'anomalies** : {data['bugs_count']}

## Liste des Anomalies Détectées
"""
        for b in data.get("bugs", []):
            md += f"### [{b.get('severity')}] {b.get('title')}\n"
            md += f"- **Spécialiste** : {b.get('specialist')} ({b.get('domain')})\n"
            md += f"- **Diagnostic** : {b.get('description')}\n"
            md += f"- **Solution C#** : `{b.get('fix')}`\n\n"

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    def _save_global_markdown(self, data: Dict[str, Any]):
        os.makedirs("reports", exist_ok=True)
        path = "reports/global_qa_report.md"
        md = f"""# Rapport Global de Certification & Audit QA

- **Score de Stabilité** : {data['quality_score']}/100 (**Grade : {data['grade']}**)
- **Durée Totale** : {data['total_duration_sec']}s
- **Total d'Anomalies Uniques** : {data['total_unique_bugs']}

## Synthèse par Niveau

| Niveau | Anomalies | Durée | Statut |
| :--- | :--- | :--- | :--- |
"""
        for lr in data.get("level_reports", []):
            st = "🔴 Critique" if lr["bugs_count"] > 5 else "🟡 Attention"
            md += f"| Niveau {lr['level_index']} | {lr['bugs_count']} bugs | {lr['duration_sec']}s | {st} |\n"

        md += "\n## Détail de Tous les Bugs Confirmés\n\n"
        for idx, b in enumerate(data.get("unique_bugs", []), 1):
            md += f"### {idx}. [{b.get('severity')}] {b.get('title')}\n"
            md += f"- **Domaine** : {b.get('domain')}\n"
            md += f"- **Diagnostic** : {b.get('description')}\n"
            md += f"- **Correctif C#** :\n```csharp\n{b.get('fix')}\n```\n\n"

        with open(path, "w", encoding="utf-8") as f:
            f.write(md)