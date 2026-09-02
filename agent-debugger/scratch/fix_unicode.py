import os

def fix_file(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # Replace emojis that fail in cp1252
    code = code.replace("\u25b6\ufe0f", "[PLAY]")
    code = code.replace("\u25b6", "[PLAY]")
    code = code.replace("[WARN]", "[WARN]")
    code = code.replace("[FAST]", "[FAST]")
    code = code.replace("[START]", "[START]")
    code = code.replace("[SCAN]", "[SCAN]")
    code = code.replace("[AI]", "[AI]")
    code = code.replace("[TARGET]", "[TARGET]")
    code = code.replace("[FIRE]", "[FIRE]")
    code = code.replace("[STOP]", "[STOP]")
    code = code.replace("[OK]", "[OK]")
    code = code.replace("[ERR]", "[ERR]")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

for root, dirs, files in os.walk(r"agent-debugger"):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))

print("Sanitized all unicode emoji prints in agent-debugger.")