using System;
using System.Collections.Generic;

namespace AIDebugger.Core
{
    public class RpcRequest
    {
        public string jsonrpc = "2.0";
        public string id;
        public string method;
        public string[] args;
        public string @params;
    }

    public class RpcResponse
    {
        public string jsonrpc = "2.0";
        public string id;
        public object result;
        public RpcError error;

        public static RpcResponse Success(string id, object result)
        {
            return new RpcResponse { id = id, result = result };
        }

        public static RpcResponse Error(string id, int code, string message, object data = null)
        {
            return new RpcResponse { id = id, error = new RpcError { code = code, message = message, data = data } };
        }
    }

    public class RpcError
    {
        public int code;
        public string message;
        public object data;
    }

    public class RpcEvent
    {
        public string @event;
        public object payload;
    }

    [Serializable]
    public class TelemetrySnapshot
    {
        public string timestamp;
        public int frameCount;
        public float timeSinceStartup;
        public float timeScale;
        public ProfilerMetrics metrics;
        public List<LogEntryDto> recentLogs = new List<LogEntryDto>();
        public List<SpatialEntity2D> entities2D = new List<SpatialEntity2D>();
        public List<SpatialEntity3D> entities3D = new List<SpatialEntity3D>();
        public List<CollisionEventDto> recentCollisions = new List<CollisionEventDto>();
        public string activeChaosScenario;
    }

    [Serializable]
    public class ProfilerMetrics
    {
        public float fps;
        public float frameTimeMs;
        public long gcMemoryBytes;
        public long totalAllocatedMemoryBytes;
        public long totalReservedMemoryBytes;
        public int activeGameObjectsCount;
        public int totalComponentsCount;
        public int drawCallsCount;
    }

    [Serializable]
    public class LogEntryDto
    {
        public string timestamp;
        public int frame;
        public string type;
        public string message;
        public string stackTrace;
        public string sourceObject;
    }

    [Serializable]
    public class SpatialEntity2D
    {
        public int instanceId;
        public string name;
        public string tag;
        public int layer;
        public bool activeInHierarchy;
        public float posX, posY;
        public float rotationZ;
        public float scaleX, scaleY;
        public float velocityX, velocityY;
        public float angularVelocity;
        public bool hasCollider2D;
        public bool isTrigger;
        public float boundsMinX, boundsMinY, boundsMaxX, boundsMaxY;
    }

    [Serializable]
    public class SpatialEntity3D
    {
        public int instanceId;
        public string name;
        public string tag;
        public int layer;
        public bool activeInHierarchy;
        public float posX, posY, posZ;
        public float rotX, rotY, rotZ, rotW;
        public float scaleX, scaleY, scaleZ;
        public float velocityX, velocityY, velocityZ;
        public float angularVelocityX, angularVelocityY, angularVelocityZ;
        public bool hasCollider;
        public bool isTrigger;
        public float boundsMinX, boundsMinY, boundsMinZ, boundsMaxX, boundsMaxY, boundsMaxZ;
    }

    [Serializable]
    public class CollisionEventDto
    {
        public string timestamp;
        public int frame;
        public string type;
        public string state;
        public int sourceInstanceId;
        public string sourceName;
        public int targetInstanceId;
        public string targetName;
        public float impactVelocity;
        public float contactPointX;
        public float contactPointY;
        public float contactPointZ;
        public string entityA;
        public string entityB;
        public float relativeVelocity;
    }

    public class GameObjectNode
    {
        public int instanceId;
        public string name;
        public string tag;
        public int layer;
        public bool activeSelf;
        public bool activeInHierarchy;
        public List<ComponentInfo> components = new List<ComponentInfo>();
        public List<GameObjectNode> children = new List<GameObjectNode>();
    }

    public class ComponentInfo
    {
        public string type;
        public string typeName;
        public string assemblyQualifiedName;
        public bool isMonoBehaviour;
        public bool isEnabled;
        public bool enabled;
        public Dictionary<string, object> fields = new Dictionary<string, object>();
        public Dictionary<string, object> properties = new Dictionary<string, object>();
    }

    public class GameObjectDetails
    {
        public int instanceId;
        public string name;
        public string tag;
        public int layer;
        public bool activeSelf;
        public bool isStatic;
        public float[] position;
        public float[] rotation;
        public float[] scale;
        public List<ComponentInfo> components = new List<ComponentInfo>();
    }

    public class DynamicCodeResult
    {
        public bool success;
        public object returnValue;
        public string output;
        public string error;
        public double executionTimeMs;
        public string logs;
    }
}