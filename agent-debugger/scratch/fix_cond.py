import os

path = r"agent-debugger\llm\llm_provider.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace condition to include NULL_REFERENCE_CASCADE and all anomalies
old_cond = 'if "nullreferenceexception" in prompt_lower or "targettransform" in prompt_lower:'
new_cond = 'if "nullreferenceexception" in prompt_lower or "targettransform" in prompt_lower or "null_reference_cascade" in prompt_lower:'
code = code.replace(old_cond, new_cond)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Restored anomaly conditions in HeuristicExpertProvider.")