import os

base_dir = r"C:\Users\timot\My project (1)\Assets\unity-debugger-bridge"
for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".cs"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                code = file.read()
            # Replace obsolete FindObjectsOfType
            code = code.replace("GameObject.FindObjectsOfType<GameObject>(true)", "UnityEngine.Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include, FindObjectsSortMode.None)")
            code = code.replace("FindObjectsOfType<TrackedObject>(true)", "FindObjectsByType<TrackedObject>(FindObjectsInactive.Include, FindObjectsSortMode.None)")
            code = code.replace("FindObjectsOfType<Rigidbody>(true)", "FindObjectsByType<Rigidbody>(FindObjectsInactive.Include, FindObjectsSortMode.None)")
            code = code.replace("FindObjectsOfType<Rigidbody2D>(true)", "FindObjectsByType<Rigidbody2D>(FindObjectsInactive.Include, FindObjectsSortMode.None)")
            code = code.replace("FindObjectsOfType<MonoBehaviour>(true)", "FindObjectsByType<MonoBehaviour>(FindObjectsInactive.Include, FindObjectsSortMode.None)")
            with open(fpath, "w", encoding="utf-8") as file:
                file.write(code)

print("Cleaned all obsolete APIs in My project (1)!")