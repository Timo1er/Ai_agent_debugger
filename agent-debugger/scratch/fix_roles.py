import os

path = r"agent-debugger\llm\llm_provider.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

old_roles = """        is_triage = "triage" in sys_lower
        is_inspector = "inspector" in sys_lower or "spatial" in sys_lower
        is_fixer = "fixer" in sys_lower or "patch" in sys_lower"""

new_roles = """        is_inspector = "inspector" in sys_lower or "spatial" in sys_lower
        is_fixer = "fixer" in sys_lower or "patch" in sys_lower
        is_triage = ("triage and log analyst" in sys_lower or "triage analyst" in sys_lower or "triage" in sys_lower) and not (is_inspector or is_fixer)"""

code = code.replace(old_roles, new_roles)
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed agent role disambiguation in llm_provider.py")