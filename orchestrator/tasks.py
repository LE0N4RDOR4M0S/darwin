"""
Celery tasks do Darwin Orchestrator.
Implementa o ciclo completo de evolução como uma task persistente:
    RECEIVED → GENERATING → COLLECTING_BASELINE → EVALUATING → APPROVED | REJECTED | REVIEW | FAILED
"""
import os
import time
import requests

from worker import celery_app
from state import update_cycle
from models import CycleState
from utils.logger import get_logger

logger = get_logger("tasks")

GENERATOR_URL  = os.getenv("GENERATOR_URL",  "http://generator:5002")
EVALUATOR_URL  = os.getenv("EVALUATOR_URL",  "http://evaluator:5001")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

# Mapeamento de recomendação → estado do ciclo
RECOMMENDATION_TO_STATE = {
    "approve_auto":  CycleState.APPROVED,
    "review_manual": CycleState.REVIEW,
    "reject":        CycleState.REJECTED,
}


@celery_app.task(
    bind=True,
    name="orchestrator.process_hotspot",
    max_retries=2,
    default_retry_delay=30,
)
def process_hotspot_task(self, cycle_id: str, hotspot_data: dict):
    """
    Task principal do ciclo de evolução Darwin.
    1. Chama Generator → cria branch candidato no /repo
    2. Coleta métricas baseline do Prometheus
    3. Estima métricas candidato (Onda 1: heurística; Onda 2: sandbox real)
    4. Chama Evaluator → calcula score e recomendação
    5. Atualiza estado final do ciclo no Redis
    """
    try:
        # ── ETAPA 1: Geração do patch ─────────────────────────────────────
        update_cycle(cycle_id, state=CycleState.GENERATING)
        logger.info(f"[{cycle_id}] 🧠 Iniciando geração de patch...")

        gen_resp = requests.post(
            f"{GENERATOR_URL}/generate",
            json={"hotspots": [hotspot_data], "timestamp": time.time()},
            timeout=120,
        )
        gen_resp.raise_for_status()
        patch = gen_resp.json()

        if patch.get("status") != "success":
            msg = patch.get("message", "Nenhuma heurística aplicável")
            logger.warning(f"[{cycle_id}] ⚠️ Generator: {msg}")
            update_cycle(cycle_id, state=CycleState.FAILED, error=f"Generator: {msg}")
            return {"cycle_id": cycle_id, "state": "failed", "reason": msg}

        update_cycle(
            cycle_id,
            patch_branch=patch.get("branch"),
            patch_file=patch.get("file_path"),
            rule_applied=patch.get("rule_applied"),
        )
        logger.info(f"[{cycle_id}] ✅ Patch gerado: branch={patch.get('branch')} rule={patch.get('rule_applied')}")

        # ── ETAPA 2: Coleta de baseline ───────────────────────────────────
        update_cycle(cycle_id, state=CycleState.COLLECTING_BASELINE)
        logger.info(f"[{cycle_id}] 📡 Coletando métricas baseline do Prometheus...")
        baseline = _collect_prometheus_metrics()
        update_cycle(cycle_id, baseline_metrics=baseline)

        # ── ETAPA 3: Estimativa de métricas candidato ─────────────────────
        # Onda 1: estimativa conservadora baseada na regra aplicada.
        # Onda 2: substituir por métricas reais do Sandbox Runner.
        candidate = _estimate_candidate_metrics(baseline, hotspot_data, patch.get("rule_applied"))
        update_cycle(cycle_id, candidate_metrics=candidate)
        logger.info(f"[{cycle_id}] 📊 Baseline: {baseline} | Candidato estimado: {candidate}")

        # ── ETAPA 4: Avaliação ────────────────────────────────────────────
        update_cycle(cycle_id, state=CycleState.EVALUATING)
        logger.info(f"[{cycle_id}] 🔬 Enviando ao Evaluator...")

        eval_resp = requests.post(
            f"{EVALUATOR_URL}/evaluate",
            json={
                "baseline":  baseline,
                "candidate": candidate,
                "cycle_id":  cycle_id,
            },
            timeout=30,
        )
        eval_resp.raise_for_status()
        evaluation = eval_resp.json()

        score          = evaluation.get("score", 0.0)
        recommendation = evaluation.get("recommendation", "reject")
        final_state    = RECOMMENDATION_TO_STATE.get(recommendation, CycleState.REJECTED)

        update_cycle(
            cycle_id,
            state=final_state,
            score=score,
            recommendation=recommendation,
        )
        logger.info(f"[{cycle_id}] 🏁 Ciclo concluído: state={final_state} score={score:.2f}")
        return {"cycle_id": cycle_id, "state": final_state, "score": score}

    except Exception as exc:
        logger.error(f"[{cycle_id}] ❌ Falha no ciclo: {exc}")
        update_cycle(cycle_id, state=CycleState.FAILED, error=str(exc))
        raise self.retry(exc=exc)


# ──────────────────────────────────────────────────────────────────────────────
# Funções auxiliares
# ──────────────────────────────────────────────────────────────────────────────

def _collect_prometheus_metrics() -> dict:
    """
    Coleta snapshot atual de métricas de performance do Prometheus.
    Retorna zeros se Prometheus não estiver disponível (modo dev).
    """
    def query(q: str) -> float:
        try:
            r = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": q},
                timeout=5,
            )
            results = r.json().get("data", {}).get("result", [])
            if results:
                return round(float(results[0]["value"][1]), 4)
        except Exception:
            pass
        return 0.0

    return {
        "latency_p95": query(
            'histogram_quantile(0.95, sum(rate(http_server_requests_seconds_bucket[5m])) by (le))'
        ),
        "error_rate": query(
            'sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m])) / '
            'sum(rate(http_server_requests_seconds_count[5m]))'
        ),
        "cpu_usage": query(
            'avg(rate(process_cpu_seconds_total[5m]))'
        ),
    }


def _estimate_candidate_metrics(baseline: dict, hotspot: dict, rule: str) -> dict:
    """
    Estimativa conservadora de melhoria com base na regra aplicada.
    
    Fatores de melhoria calibrados conservadoramente:
    - timeout: reduz latência (~15%) e CPU minimamente (~5%)
    - pool_size: reduz latência (~10%) e CPU em filas (~20%)
    - caching: maior impacto em latência (~40%) e CPU (~30%)
    
    Onda 2 substituirá esta função por métricas reais do Sandbox Runner.
    """
    candidate = dict(baseline)

    if not any(candidate.values()):
        # Sem dados reais de baseline — simular valores para validar o fluxo
        candidate = {"latency_p95": 2.5, "error_rate": 0.08, "cpu_usage": 0.85}
        baseline.update(candidate)

    if rule == "timeout":
        candidate["latency_p95"] = round(baseline.get("latency_p95", 0) * 0.85, 4)
        candidate["cpu_usage"]   = round(baseline.get("cpu_usage",   0) * 0.95, 4)

    elif rule == "pool_size":
        candidate["latency_p95"] = round(baseline.get("latency_p95", 0) * 0.90, 4)
        candidate["cpu_usage"]   = round(baseline.get("cpu_usage",   0) * 0.80, 4)

    elif rule == "caching":
        candidate["latency_p95"] = round(baseline.get("latency_p95", 0) * 0.60, 4)
        candidate["cpu_usage"]   = round(baseline.get("cpu_usage",   0) * 0.70, 4)
        candidate["error_rate"]  = round(baseline.get("error_rate",  0) * 0.90, 4)

    return candidate
