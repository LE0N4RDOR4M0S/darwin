from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Recommendation(str, Enum):
    APPROVE_AUTO = "approve_auto"
    REVIEW_MANUAL = "review_manual"
    REJECT = "reject"


class MetricsSnapshot(BaseModel):
    """Snapshot de métricas coletadas do Prometheus em um dado momento."""
    latency_p95: float = 0.0   # segundos
    error_rate: float = 0.0    # 0.0 a 1.0
    cpu_usage: float = 0.0     # 0.0 a 1.0


class EvaluationRequest(BaseModel):
    baseline: MetricsSnapshot
    candidate: MetricsSnapshot
    cycle_id: Optional[str] = None


class EvaluationResult(BaseModel):
    score: float
    recommendation: Recommendation
    delta_latency_pct: float
    delta_error_pct: float
    delta_cpu_pct: float
    confidence: float
    report: dict
    cycle_id: Optional[str] = None
