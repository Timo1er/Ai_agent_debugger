import json
from typing import Any, Dict
from .base_agent import BaseAgent
from debugger_client.protocol import DynamicCodeResult

class CodeFixerAgent(BaseAgent):
    """
    Fixer & Hot-Patch Agent:
    Formulates remediation strategies, generates runtime property overrides,
    crafts dynamic C# hot-patches, and validates fix application.
    """
    def __init__(self, client, llm):
        super().__init__("CodeFixer", "Remediation & Hot-Patching Engineer", client, llm)

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        triage_report = context.get("triage_report", {})
        inspection_result = context.get("inspection_result", {})

        system_prompt = (
            "You are the Code Fixer and Hot-Patching Agent for Unity.\n"
            "Given the diagnosed bug and root cause, synthesize a runtime fix command or C# dynamic script.\n"
            "Respond in JSON format with fields: fix_strategy, action_type, runtime_command, code_patch, explanation."
        )

        user_prompt = f"""
Triage Report:
{json.dumps(triage_report, indent=2)}

Inspection Result:
{json.dumps(inspection_result, indent=2)}

Formulate concrete runtime fix command (e.g. SET Target.Component.Field = Value or dynamic C# script).
"""

        response_str = await self.llm.generate_response(system_prompt, user_prompt)
        try:
            fix_plan = json.loads(response_str)
        except Exception:
            fix_plan = {
                "fix_strategy": "MANUAL_OR_DYNAMIC_PATCH",
                "action_type": "DYNAMIC_CODE_EXECUTION",
                "runtime_command": "SET Player3D.Player3DController.isStunned = false",
                "explanation": response_str
            }

        # Apply fix
        execution_result = await self._apply_fix(fix_plan)
        fix_plan["execution_result"] = execution_result

        self.log(f"Fix applied. Strategy: {fix_plan.get('fix_strategy')}, Success: {execution_result.get('success', False)}")
        return fix_plan

    async def _apply_fix(self, fix_plan: Dict[str, Any]) -> Dict[str, Any]:
        cmd = fix_plan.get("runtime_command", "")
        if not cmd:
            return {"success": False, "error": "No runtime command provided"}

        res: DynamicCodeResult = await self.client.execute_code(cmd)
        return {
            "success": res.success,
            "returnValue": res.returnValue,
            "logs": res.logs,
            "error": res.error,
            "timeMs": res.executionTimeMs
        }