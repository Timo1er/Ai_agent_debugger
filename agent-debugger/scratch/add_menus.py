import os

files = {
    r"C:\Users\timot\My project\Assets\Scripts\Telemetry\TelemetryServer.cs": 'TelemetryServer',
    r"C:\Users\timot\My project\Assets\Scripts\Core\GameBootstrapper.cs": 'GameBootstrapper',
    r"C:\Users\timot\My project\Assets\Scripts\Telemetry\MetricsCollector.cs": 'MetricsCollector',
    r"C:\Users\timot\My project\Assets\Scripts\Core\RemotePatcher.cs": 'RemotePatcher',
    r"C:\Users\timot\My project\Assets\Scripts\Bugs\BugInjector.cs": 'BugInjector'
}

for path, class_name in files.items():
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "AddComponentMenu" not in content:
            content = content.replace(f"public class {class_name}", f'[AddComponentMenu("AI Debugger/{class_name}")]\npublic class {class_name}')
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Added AddComponentMenu to {class_name}")