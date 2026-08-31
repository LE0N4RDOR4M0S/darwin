from utils.logger import get_logger

logger = get_logger("scoring")


def evaluate_metrics(baseline: dict, candidate: dict) -> dict:
    """
    Calcula o delta percentual entre baseline e candidate para cada métrica:
      - delta = (baseline - candidate) / baseline * 100
      - delta positivo = melhoria
      - delta negativo = regressão

    Score ponderado:
      - Latência P95: 50%
      - Error Rate: 30%
      - CPU Usage: 20%

    Guarda zero-baseline: se baseline não contiver dados válidos, rejeita o patch.
    """
    b_lat = baseline.get("latency_p95", 0.0)
    c_lat = candidate.get("latency_p95", 0.0)
    b_err = baseline.get("error_rate", 0.0)
    c_err = candidate.get("error_rate", 0.0)
    b_cpu = baseline.get("cpu_usage", 0.0)
    c_cpu = candidate.get("cpu_usage", 0.0)

    # Zero-baseline guard
    if not any([b_lat, b_err, b_cpu]):
        logger.warning("⚠️ Baseline zerado ou inválido. Rejeitando patch por falta de dados.")
        return {
            "score": 0.0,
            "decision": "reject",
            "delta_latency_pct": 0.0,
            "delta_error_pct": 0.0,
            "delta_cpu_pct": 0.0,
            "confidence": 0.0,
            "reason": "Invalid or zero baseline",
        }

    delta_lat = ((b_lat - c_lat) / b_lat * 100.0) if b_lat > 0 else 0.0
    delta_err = ((b_err - c_err) / b_err * 100.0) if b_err > 0 else 0.0
    delta_cpu = ((b_cpu - c_cpu) / b_cpu * 100.0) if b_cpu > 0 else 0.0

    score = round(delta_lat * 0.5 + delta_err * 0.3 + delta_cpu * 0.2, 2)

    # Determinar recomendação
    if score >= 10.0:
        decision = "approve_auto"
    elif score > 0.0:
        decision = "review_manual"
    else:
        decision = "reject"

    # Confiança baseada na magnitude e consistência dos sinais
    signals = [s for s in [delta_lat, delta_err, delta_cpu] if s != 0.0]
    confidence = round(min(1.0, len(signals) / 3.0 * (1.0 if score > 0 else 0.5)), 2)

    result = {
        "score": score,
        "decision": decision,
        "delta_latency_pct": round(delta_lat, 2),
        "delta_error_pct": round(delta_err, 2),
        "delta_cpu_pct": round(delta_cpu, 2),
        "confidence": confidence,
        "baseline": baseline,
        "candidate": candidate,
    }

    logger.info(f"✅ Avaliação concluída | Score={score:.2f} | Decisão={decision} | Confidence={confidence}")
    return result
