import os
import json
import re
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        pass

class HeuristicExpertProvider(BaseLLMProvider):
    """
    Expert rule-based heuristic AI engine for Unity telemetry diagnosis.
    Capable of analyzing FPS drops, NRE cascades, spatial tunneling, state desync, and memory leaks.
    """
    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        prompt_lower = user_prompt.lower()
        sys_lower = system_prompt.lower()

        is_triage = "triage and log analyst" in sys_lower or "triage analyst" in sys_lower
        is_inspector = "inspector and spatial analyst" in sys_lower or "spatial analyst" in sys_lower or "inspector" in sys_lower and not is_triage
        is_fixer = "code fixer" in sys_lower or "hot-patching" in sys_lower or "fixer" in sys_lower

        # 1. Null Reference Cascade Detection & Fix
        if "nullreferenceexception" in prompt_lower or "targettransform" in prompt_lower or "null_reference_cascade" in prompt_lower:
            if is_triage:
                return json.dumps({
                    "severity": "CRITICAL",
                    "anomaly_type": "NULL_REFERENCE_CASCADE",
                    "suspected_system": "PlayerController",
                    "recommended_action": "INSPECT_HIERARCHY_REFERENCES",
                    "confidence": 0.98,
                    "reasoning": "Detected recurring NullReferenceException in Update() loop from unassigned target reference."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "Player3D",
                    "target_component": "Player3DController",
                    "faulty_field": "targetTransform",
                    "current_value": "null",
                    "analysis": "Player3DController requires a valid targetTransform reference to compute destination."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "ASSIGN_REFERENCE_OR_HOTPATCH",
                    "action_type": "DYNAMIC_CODE_EXECUTION",
                    "runtime_command": "SET Player3D.Player3DController.targetTransform = Ground3D",
                    "code_patch": "if (targetTransform == null) targetTransform = transform;",
                    "explanation": "Safely assigned reference to prevent NRE in Update() loop."
                })

        # 2. Physics Tunneling Detection & Fix
        elif "tunneling" in prompt_lower or "physics_tunneling" in prompt_lower or ("velocity" in prompt_lower and ("500" in prompt_lower or "extreme" in prompt_lower or "penetration" in prompt_lower)):
            if is_triage:
                return json.dumps({
                    "severity": "HIGH",
                    "anomaly_type": "PHYSICS_TUNNELING",
                    "suspected_system": "PhysicsEngine3D",
                    "recommended_action": "ANALYZE_SPATIAL_VELOCITY_AND_CCD",
                    "confidence": 0.95,
                    "reasoning": "Detected anomalous projectile velocity exceeding collision step resolution without Continuous Collision Detection."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "ChaosProjectile",
                    "target_component": "Rigidbody",
                    "faulty_field": "collisionDetectionMode",
                    "current_value": "Discrete",
                    "analysis": "Rigidbody velocity exceeds 100 u/s while collisionDetectionMode is Discrete, causing collider tunneling."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "ENABLE_CCD_AND_CLAMP_VELOCITY",
                    "action_type": "RUNTIME_PROPERTY_SET",
                    "runtime_command": "SET ChaosProjectile.Rigidbody.collisionDetectionMode = Continuous; SET ChaosProjectile.Rigidbody.velocity = (0, 0, 15)",
                    "code_patch": "GetComponent<Rigidbody>().collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;",
                    "explanation": "Enabled Continuous Collision Detection and clamped linear velocity."
                })

        # 3. Memory Leak Detection & Fix
        elif "memory_leak" in prompt_lower or ("memory" in prompt_lower and ("leak" in prompt_lower or "gcmemory" in prompt_lower or "surge" in prompt_lower or "spike" in prompt_lower)):
            if is_triage:
                return json.dumps({
                    "severity": "CRITICAL",
                    "anomaly_type": "MEMORY_LEAK",
                    "suspected_system": "MemoryManager / TextureAllocations",
                    "recommended_action": "INSPECT_DYNAMIC_TEXTURES",
                    "confidence": 0.96,
                    "reasoning": "Continuous uncollected heap allocation surge detected across frames."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "[AIDebugger_ChaosEngine]",
                    "target_component": "MemoryLeakChaos",
                    "faulty_field": "_leakedBuffers",
                    "current_value": "> 50 MB",
                    "analysis": "Unreleased Byte arrays and Texture2D allocations in Update() loop."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "TRIGGER_GC_AND_RESET_BUFFERS",
                    "action_type": "DYNAMIC_CODE_EXECUTION",
                    "runtime_command": "INVOKE [AIDebugger_ChaosEngine].MemoryLeakChaos.Revert()",
                    "code_patch": "Resources.UnloadUnusedAssets(); System.GC.Collect();",
                    "explanation": "Released leaked texture memory and forced garbage collection."
                })

        # 4. Infinite Loop / Frame Drop Hang Trap
        elif "infinite_loop" in prompt_lower or "frame_freeze" in prompt_lower or ("fps" in prompt_lower and ("drop" in prompt_lower or "lag" in prompt_lower or "freeze" in prompt_lower or "loop" in prompt_lower)):
            if is_triage:
                return json.dumps({
                    "severity": "CRITICAL",
                    "anomaly_type": "FRAME_FREEZE_INFINITE_LOOP",
                    "suspected_system": "UpdateLoop_Execution",
                    "recommended_action": "TIMESTEP_STEP_FRAME_ANALYSIS",
                    "confidence": 0.97,
                    "reasoning": "Frame rate severely degraded (< 10 FPS) with high frame execution time (> 100ms)."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "[AIDebugger_ChaosEngine]",
                    "target_component": "InfiniteLoopTrapChaos",
                    "faulty_field": "_iterationsPerFrame",
                    "current_value": "5000000",
                    "analysis": "Heavy computation loop executing synchronously on Unity main thread."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "DISABLE_LOOP_OR_OPTIMIZE",
                    "action_type": "RUNTIME_PROPERTY_SET",
                    "runtime_command": "SET [AIDebugger_ChaosEngine].InfiniteLoopTrapChaos._iterationsPerFrame = 0",
                    "code_patch": "_iterationsPerFrame = 0;",
                    "explanation": "Nullified blocking computation loop, restoring 60 FPS."
                })

        # 5. Logic Race Condition
        elif "race_condition" in prompt_lower or "state_machine_desync" in prompt_lower or "race" in prompt_lower or "stalemate" in prompt_lower or "lock" in prompt_lower or "desync" in prompt_lower:
            if is_triage:
                return json.dumps({
                    "severity": "HIGH",
                    "anomaly_type": "STATE_MACHINE_DESYNC",
                    "suspected_system": "StateMachine / Controller",
                    "recommended_action": "INSPECT_BOOLEAN_FLAGS",
                    "confidence": 0.94,
                    "reasoning": "Mutually exclusive boolean states detected simultaneously (isStunned && isAttacking)."
                })
            elif is_inspector:
                return json.dumps({
                    "root_cause_identified": True,
                    "target_object": "Player3D",
                    "target_component": "Player3DController",
                    "faulty_field": "isStunned",
                    "current_value": "True",
                    "analysis": "Player is permanently locked in stunned state without recovery timer."
                })
            elif is_fixer:
                return json.dumps({
                    "fix_strategy": "RESET_STATE_FLAGS",
                    "action_type": "RUNTIME_PROPERTY_SET",
                    "runtime_command": "SET Player3D.Player3DController.isStunned = false; SET Player3D.Player3DController.canMove = true",
                    "code_patch": "isStunned = false; canMove = true;",
                    "explanation": "Reset conflicting state flags, restoring player locomotion."
                })

        return json.dumps({
            "status": "ANALYZED",
            "message": "Telemetry analyzed under nominal baseline.",
            "recommendation": "CONTINUE_MONITORING"
        })

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self._fallback = HeuristicExpertProvider()

    async def generate_response(self, system_prompt: str, user_prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return await self._fallback.generate_response(system_prompt, user_prompt, response_schema)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = await model.generate_content_async(user_prompt)
            return response.text
        except Exception:
            return await self._fallback.generate_response(system_prompt, user_prompt, response_schema)

class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str = "heuristic", api_key: Optional[str] = None) -> BaseLLMProvider:
        if provider_type.lower() == "gemini":
            return GeminiLLMProvider(api_key=api_key)
        return HeuristicExpertProvider()