import os

path = r"agent-debugger\llm\llm_provider.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix target_object to Player3D
code = code.replace('"target_object": "Player"', '"target_object": "Player3D"')
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated HeuristicExpertProvider target_object.")