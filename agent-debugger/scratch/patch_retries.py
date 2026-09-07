import os

cl_path = r"agent-debugger\debugger_client\unity_client.py"
with open(cl_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("def connect(self, timeout: float = 3.0, retries: int = 6)", "def connect(self, timeout: float = 2.0, retries: int = 12)")
with open(cl_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated unity_client.py with 12 retries connection loop.")