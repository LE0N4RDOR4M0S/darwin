from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import time


class HotspotType(str, Enum):
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"


class HotspotInput(BaseModel):
    type: HotspotType
    endpoint: Optional[str] = None
    instance: Optional[str] = None
    value: float
    threshold: float
    timestamp: Optional[float] = None


class GenerationRequest(BaseModel):
    """Payload recebido pelo Generator vindo do Orchestrator (via tasks.py)."""
    hotspots: list[HotspotInput]
    timestamp: float = Field(default_factory=time.time)


class PatchResult(BaseModel):
    """Resultado de uma tentativa de geração de patch."""
    status: str  # "success" | "skipped" | "no_applicable_rule" | "error"
    branch: Optional[str] = None
    file_path: Optional[str] = None
    rule_applied: Optional[str] = None
    message: Optional[str] = None
