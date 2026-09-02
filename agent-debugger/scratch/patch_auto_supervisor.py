import os

sup_path = r"agent-debugger\agents\multi_agent_supervisor.py"
with open(sup_path, "r", encoding="utf-8") as f:
    code = f.read()

# Make supervisor autonomously use GodMode, Teleport, Fly, and Reset
old_start = """        await self._update_unity_hud("Superviseur IA", "Audit Gameplay Approfondi", "Déploiement des règles d'inspection")
        try:
            if hasattr(self.client, "start_player_exploration"):
                await self.client.start_player_exploration(duration=self.duration_seconds)
        except Exception:
            pass"""

new_start = """        await self._update_unity_hud("Superviseur IA", "Audit Gameplay & Pouvoirs Game Master", "Activation autonome de l'invulnérabilité")
        
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
            pass"""

code = code.replace(old_start, new_start)

# Add autonomous teleportation during Phase 3
old_p3 = """        # === 3. STRESS PHYSIQUE D'ANGLES AIGUS ===
        print(f"\\n[PHASE 3/5] [PHYSICAL STRESS LAB] Fuzzing d'impacts & tests de collision...")"""

new_p3 = """        # === 3. STRESS PHYSIQUE, TÉLÉPORTATION AUTONOME & COLLISION FUZZING ===
        print(f"\\n[PHASE 3/5] [PHYSICAL STRESS LAB] Téléportation autonome multi-secteurs & Fuzzing...")
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
            pass"""

code = code.replace(old_p3, new_p3)

with open(sup_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated multi_agent_supervisor.py with fully autonomous Game Master powers.")