from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import time


class HotspotType(str, Enum):
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"


class Hotspot(BaseModel):
    type: HotspotType
    endpoint: Optional[str] = None
    instance: Optional[str] = None
    value: float
    threshold: float
    timestamp: float = Field(default_factory=time.time)


class HotspotEvent(BaseModel):
    """Payload enviado do Detector ao Orchestrator."""
    hotspots: list[Hotspot]
    timestamp: float = Field(default_factory=time.time)


class DetectionResult(BaseModel):
    hotspots: list[Hotspot]
    scan_timestamp: float = Field(default_factory=time.time)
    prometheus_url: str
