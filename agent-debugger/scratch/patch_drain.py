import os

sup_path = r"agent-debugger\agents\multi_agent_supervisor.py"
with open(sup_path, "r", encoding="utf-8") as f:
    code = f.read()

drain_code = """        # === RÉCOLTE FINALE DE TOUS LES ÉVÉNEMENTS DE TUNNELING & COLLISIONS SUR LA DURÉE TOTALE ===
        print(f"\\n[SYNTHESE] Récolte des événements de collision et sentinelles physiques...")
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
                            "fix": "1. Passer Rigidbody2D.collisionDetectionMode en Continuous.\\n2. Remplacer les téléportations Dash (transform.position += ...) par des impulsions physiques Rigidbody2D.AddForce."
                        })
                        print(f"   -> [COLLISION DETECTEE] [CRITICAL] {title}")
        except Exception as ex:
            print(f"   -> Tunneling harvest: {ex}")

        total_time = time.perf_counter() - t_start"""

if "[SYNTHESE] Récolte des événements" not in code:
    code = code.replace("total_time = time.perf_counter() - t_start", drain_code)
    with open(sup_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated multi_agent_supervisor.py with final collision & tunneling harvest.")