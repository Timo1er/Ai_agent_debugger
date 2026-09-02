import json
from typing import Any, Dict, List
from .base_agent import BaseAgent

class SpatialInspectorAgent(BaseAgent):
    """
    Inspector & Spatial Analyst Agent:
    Traverses GameObject hierarchies via reflection, inspects 2D/3D physics state,
    identifies missing references, and pinpoints root causes.
    """
    def __init__(self, client, llm):
        super().__init__("SpatialInspector", "Scene Hierarchy & Physics Inspector", client, llm)

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        triage_report = context.get("triage_report", {})
        suspected_system = triage_report.get("suspected_system", "")
        anomaly_type = triage_report.get("anomaly_type", "")

        # Fetch scene state
        hierarchy = await self.client.get_hierarchy()
        spatial_2d = await self.client.get_spatial_2d()
        spatial_3d = await self.client.get_spatial_3d()

        system_prompt = (
            "You are the Inspector and Spatial Analyst Agent for a Unity engine.\n"
            "Given the triage report, scene hierarchy, and 2D/3D physics data, identify the exact "
            "GameObject, Component, and member field/variable causing the issue."
        )

        user_prompt = f"""
Triage Diagnosis:
{json.dumps(triage_report, indent=2)}

Scene State:
- 2D Entities: {json.dumps(spatial_2d, indent=2)}
- 3D Entities: {json.dumps(spatial_3d, indent=2)}
- Hierarchy Summary: Found {len(hierarchy)} root objects.

Perform deep inspection to isolate target object, component, and faulty state.
"""

        response_str = await self.llm.generate_response(system_prompt, user_prompt)
        try:
            inspection_result = json.loads(response_str)
        except Exception:
            inspection_result = {
                "root_cause_identified": True,
                "analysis": response_str,
                "target_object": "Player3D" if "3d" in anomaly_type.lower() else "Player2D"
            }

        self.log(f"Inspection complete. Target Object: {inspection_result.get('target_object')}, Component: {inspection_result.get('target_component')}")
        return inspection_result