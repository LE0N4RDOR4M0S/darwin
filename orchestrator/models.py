from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import uuid
import time


class CycleState(str, Enum):
    """Estados possíveis de um ciclo de evolução (FSM)."""
    RECEIVED           = "received"
    GENERATING         = "generating"
    COLLECTING_BASELINE = "collecting_baseline"
    EVALUATING         = "evaluating"
    APPROVED           = "approved"
    REJECTED           = "rejected"
    REVIEW             = "review"
    FAILED             = "failed"


class HotspotData(BaseModel):
    """Representação de um hotspot dentro do Orchestrator."""
    type: str
    endpoint: Optional[str] = None
    instance: Optional[str] = None
    value: float
    threshold: float
    timestamp: Optional[float] = None


class HotspotEvent(BaseModel):
    """Payload recebido do Detector."""
    hotspots: list[HotspotData]
    timestamp: float = Field(default_factory=time.time)


class CycleRecord(BaseModel):
    """Registro completo de um ciclo de evolução, persistido no Redis."""
    cycle_id:          str        = Field(default_factory=lambda: str(uuid.uuid4()))
    state:             CycleState = CycleState.RECEIVED
    hotspot:           Optional[HotspotData] = None

    # Geração
    patch_branch:  Optional[str] = None
    patch_file:    Optional[str] = None
    rule_applied:  Optional[str] = None

    # Avaliação
    baseline_metrics:  Optional[dict] = None
    candidate_metrics: Optional[dict] = None
    score:             Optional[float] = None
    recommendation:    Optional[str]  = None

    # Diagnóstico
    error: Optional[str] = None

    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
