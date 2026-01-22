from utils.logger import get_logger

logger = get_logger("scoring")

def evaluate_metrics(baseline: dict, candidate: dict) -> dict:
    b_latency = baseline.get("latency_p95", 0)
    c_latency = candidate.get("latency_p95", 0)
    b_error = baseline.get("error_rate", 0)
    c_error = candidate.get("error_rate", 0)
    b_cpu = baseline.get("cpu_usage", 0)
    c_cpu = candidate.get("cpu_usage", 0)

    delta_latency = ((b_latency - c_latency) / b_latency * 100) if b_latency else 0
    delta_error = ((b_error - c_error) / b_error * 100) if b_error else 0
    delta_cpu = ((b_cpu - c_cpu) / b_cpu * 100) if b_cpu else 0

    score = (
        delta_latency * 0.5 +
        delta_error * 0.3 +
        delta_cpu * 0.2
    )

    if score > 10:
        decision = "approve_auto"
    elif score > 0:
        decision = "review_manual"
    else:
        decision = "reject"

    result = {
        "baseline": baseline,
        "candidate": candidate,
        "delta_latency(%)": round(delta_latency, 2),
        "delta_error(%)": round(delta_error, 2),
        "delta_cpu(%)": round(delta_cpu, 2),
        "score": round(score, 2),
        "decision": decision
    }

    logger.info(f"✅ Avaliação concluída | Score={score:.2f} | Decisão={decision}")
    return result
