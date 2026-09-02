from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class RpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Optional[str] = None

class RpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class RpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Any] = None
    error: Optional[RpcError] = None

class ProfilerMetrics(BaseModel):
    fps: float = 60.0
    frameTimeMs: float = 16.6
    gcMemoryBytes: int = 0
    totalAllocatedMemoryBytes: int = 0
    totalReservedMemoryBytes: int = 0
    activeGameObjectsCount: int = 0
    totalComponentsCount: int = 0
    drawCallsCount: int = 0

class LogEntryDto(BaseModel):
    timestamp: str = ""
    frame: int = 0
    type: str = "Log" # Log, Warning, Error, Assert, Exception
    message: str = ""
    stackTrace: str = ""
    sourceObject: Optional[str] = None

class SpatialEntity2D(BaseModel):
    instanceId: int
    name: str
    tag: str = "Untagged"
    layer: int = 0
    activeInHierarchy: bool = True
    posX: float = 0.0
    posY: float = 0.0
    rotationZ: float = 0.0
    scaleX: float = 1.0
    scaleY: float = 1.0
    velocityX: float = 0.0
    velocityY: float = 0.0
    angularVelocity: float = 0.0
    hasCollider2D: bool = False
    isTrigger: bool = False
    boundsMinX: float = 0.0
    boundsMinY: float = 0.0
    boundsMaxX: float = 0.0
    boundsMaxY: float = 0.0

class SpatialEntity3D(BaseModel):
    instanceId: int
    name: str
    tag: str = "Untagged"
    layer: int = 0
    activeInHierarchy: bool = True
    posX: float = 0.0
    posY: float = 0.0
    posZ: float = 0.0
    rotX: float = 0.0
    rotY: float = 0.0
    rotZ: float = 0.0
    rotW: float = 1.0
    scaleX: float = 1.0
    scaleY: float = 1.0
    scaleZ: float = 1.0
    velocityX: float = 0.0
    velocityY: float = 0.0
    velocityZ: float = 0.0
    angularVelocityX: float = 0.0
    angularVelocityY: float = 0.0
    angularVelocityZ: float = 0.0
    hasCollider: bool = False
    isTrigger: bool = False
    boundsMinX: float = 0.0
    boundsMinY: float = 0.0
    boundsMinZ: float = 0.0
    boundsMaxX: float = 0.0
    boundsMaxY: float = 0.0
    boundsMaxZ: float = 0.0

class CollisionEventDto(BaseModel):
    timestamp: str = ""
    frame: int = 0
    type: str = ""
    state: str = ""
    sourceInstanceId: int = 0
    sourceName: str = ""
    targetInstanceId: int = 0
    targetName: str = ""
    impactVelocity: float = 0.0
    contactPointX: float = 0.0
    contactPointY: float = 0.0
    contactPointZ: float = 0.0

class ComponentInfo(BaseModel):
    typeName: str
    assemblyQualifiedName: Optional[str] = None
    enabled: bool = True
    fields: Dict[str, Any] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)

class GameObjectNode(BaseModel):
    instanceId: int
    name: str
    tag: str = "Untagged"
    layer: int = 0
    activeSelf: bool = True
    activeInHierarchy: bool = True
    components: List[ComponentInfo] = Field(default_factory=list)
    children: List["GameObjectNode"] = Field(default_factory=list)

class DynamicCodeResult(BaseModel):
    success: bool
    returnValue: Optional[Any] = None
    logs: Optional[str] = None
    error: Optional[str] = None
    executionTimeMs: float = 0.0

class TelemetrySnapshot(BaseModel):
    timestamp: str = ""
    frameCount: int = 0
    timeSinceStartup: float = 0.0
    timeScale: float = 1.0
    metrics: Optional[ProfilerMetrics] = None
    recentLogs: List[LogEntryDto] = Field(default_factory=list)
    entities2D: List[SpatialEntity2D] = Field(default_factory=list)
    entities3D: List[SpatialEntity3D] = Field(default_factory=list)
    recentCollisions: List[CollisionEventDto] = Field(default_factory=list)
    activeChaosScenario: Optional[str] = None