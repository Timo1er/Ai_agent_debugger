import os

def clean_bom_in_dir(target_dir):
    if not os.path.exists(target_dir):
        return
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".cs"):
                continue
            path = os.path.join(root, file)
            with open(path, "rb") as f:
                content = f.read()

            # Remove UTF-8 BOM \xef\xbb\xbf anywhere at the beginning or middle
            content_str = content.decode("utf-8-sig", errors="replace")
            content_str = content_str.replace("\ufeff", "")

            with open(path, "w", encoding="utf-8") as f:
                f.write(content_str)

clean_bom_in_dir(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge")
clean_bom_in_dir(r"C:\Users\timot\My project (1)\Assets\AIDebuggerBridge")
clean_bom_in_dir(r"c:\Users\timot\Documents\Git dev\AI-agent-debugger\unity-debugger-bridge")
print("Cleaned all BOM characters.")