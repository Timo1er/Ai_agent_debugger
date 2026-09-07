import os
import json
import re
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

# Tentative de chargement du fichier .env
def _load_env_file():
    for env_path in [".env", "agent-debugger/.env", os.path.expanduser("~/.env")]:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("\"'")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

_load_env_file()

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        pass

class HeuristicExpertProvider(BaseLLMProvider):
    """
    Moteur de diagnostic expert basé sur des règles heuristiques (fallback autonome hors ligne).
    """
    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        prompt_lower = user_prompt.lower()
        sys_lower = system_prompt.lower()

        is_inspector = "inspector" in sys_lower or "spatial" in sys_lower
        is_fixer = "fixer" in sys_lower or "patch" in sys_lower
        is_triage = ("triage and log analyst" in sys_lower or "triage analyst" in sys_lower or "triage" in sys_lower) and not (is_inspector or is_fixer)

        # 1. Null Reference Cascade
        if "nullreferenceexception" in prompt_lower or "targettransform" in prompt_lower or "null_reference_cascade" in prompt_lower:
            if is_triage:
                return json.dumps({
                    "severity": "CRITICAL",
                    "anomaly_type": "NULL_REFERENCE_CASCADE",
                    "suspected_system": "PlayerController",
                    "recommended_action": "INSPECT_HIERARCHY_REFERENCES",
                    "confidence": 0.98,
                    "reasoning": "Detected recurring NullReferenceException in Update() loop."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "Player3D",
                    "target_component": "PlayerController",
                    "faulty_field": "targetTransform",
                    "current_value": "null",
                    "analysis": "PlayerController requires a valid targetTransform reference."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "ASSIGN_REFERENCE_OR_HOTPATCH",
                    "action_type": "DYNAMIC_CODE_EXECUTION",
                    "runtime_command": "SET Player.PlayerController.targetTransform = Ground",
                    "code_patch": "if (targetTransform == null) targetTransform = transform;",
                    "explanation": "Safely assigned reference to prevent NRE."
                })

        # 2. Physics Tunneling
        elif "tunneling" in prompt_lower or "wall" in prompt_lower or "collision" in prompt_lower:
            if is_triage:
                return json.dumps({
                    "severity": "CRITICAL",
                    "anomaly_type": "PHYSICS_TUNNELING",
                    "suspected_system": "PhysicsEngine2D_3D",
                    "recommended_action": "ENABLE_CONTINUOUS_COLLISION_DETECTION",
                    "confidence": 0.96,
                    "reasoning": "Detected anomalous penetration through solid colliders."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "Player3D",
                    "target_component": "Rigidbody2D",
                    "faulty_field": "collisionDetectionMode",
                    "current_value": "Discrete",
                    "analysis": "Velocity delta caused collider tunneling."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "ENABLE_CCD",
                    "action_type": "RUNTIME_PROPERTY_SET",
                    "runtime_command": "SET Player.Rigidbody2D.collisionDetectionMode = Continuous",
                    "code_patch": "rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;",
                    "explanation": "Enabled Continuous Collision Detection to prevent tunneling."
                })

        return json.dumps({
            "status": "ANALYZED",
            "message": "Telemetry analyzed under nominal baseline.",
            "recommendation": "CONTINUE_MONITORING"
        })

class GeminiLLMProvider(BaseLLMProvider):
    """
    Fournisseur d'IA officiel Google Gemini (SDK google.genai et google.generativeai).
    Prend en charge Gemini 2.5 Flash, Gemini 2.0 Flash, Gemini 1.5 Pro avec streaming et sorties JSON structurées.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self._fallback = HeuristicExpertProvider()
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                print(f"[Gemini-AI] Client Google GenAI initialisé avec succès (Modèle: {self.model_name})")
            except Exception as ex:
                print(f"[Gemini-AI] Note SDK: {ex}")

    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return await self._fallback.generate_response(system_prompt, user_prompt, response_schema)

        # 1. Utilisation du nouveau SDK google.genai
        if self._client is not None:
            try:
                import asyncio
                from google.genai import types

                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                )
                if response_schema:
                    config.response_mime_type = "application/json"

                # Appel asynchrone / threadpool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._client.models.generate_content(
                        model=self.model_name,
                        contents=user_prompt,
                        config=config
                    )
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text
            except Exception as ex:
                print(f"[Gemini-AI] Erreur appel google.genai ({ex}), tentative fallback...")

        # 2. Fallback google.generativeai
        try:
            import google.generativeai as gai
            gai.configure(api_key=self.api_key)
            model = gai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_prompt
            )
            resp = await model.generate_content_async(user_prompt)
            if resp and resp.text:
                return resp.text
        except Exception:
            pass

        # 3. Fallback Heuristique
        return await self._fallback.generate_response(system_prompt, user_prompt, response_schema)

class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str = "auto", api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash") -> BaseLLMProvider:
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        # Si le mode est 'auto' ou 'gemini' et qu'une clé API Gemini est détectée
        if (provider_type.lower() in ["gemini", "auto"]) and key:
            return GeminiLLMProvider(api_key=key, model_name=model_name)
        elif provider_type.lower() == "gemini":
            print("[Gemini-AI] AVERTISSEMENT : Aucune clé GEMINI_API_KEY trouvée dans l'environnement ou .env. Utilisation du moteur heuristique.")
            return GeminiLLMProvider(api_key=None, model_name=model_name)

        return HeuristicExpertProvider()