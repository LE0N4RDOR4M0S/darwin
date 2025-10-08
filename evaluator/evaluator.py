from fastapi import FastAPI, UploadFile, File, HTTPException
import json, os

app = FastAPI(title="Código Vivo - Evaluator")

# Thresholds configuráveis via env vars (valores percentuais)
P95_IMPROVEMENT_AUTO = float(os.getenv('P95_IMPROVEMENT_AUTO', '5.0'))
P95_IMPROVEMENT_MANUAL = float(os.getenv('P95_IMPROVEMENT_MANUAL', '0.0'))
# Tolerância de aumento de error_rate em pontos percentuais (ex: 0.01 = 1%)
ERROR_RATE_INCREASE_TOLERANCE = float(os.getenv('ERROR_RATE_INCREASE_TOLERANCE', '0.0'))


def validate_metrics(d: dict, name: str):
    if not isinstance(d, dict):
        raise HTTPException(status_code=400, detail=f"{name} must be a JSON object")
    for k in ('p95', 'error_rate'):
        if k not in d:
            raise HTTPException(status_code=400, detail=f"{name} missing required key: {k}")
        try:
            float(d[k])
        except Exception:
            raise HTTPException(status_code=400, detail=f"{name} key {k} must be numeric")


@app.post("/evaluate")
async def evaluate(baseline: UploadFile = File(...), candidate: UploadFile = File(...)):
    try:
        b = json.loads(await baseline.read())
    except Exception:
        raise HTTPException(status_code=400, detail="Baseline is not valid JSON")
    try:
        c = json.loads(await candidate.read())
    except Exception:
        raise HTTPException(status_code=400, detail="Candidate is not valid JSON")

    validate_metrics(b, 'baseline')
    validate_metrics(c, 'candidate')

    # Calculos
    try:
        b_p95 = float(b['p95'])
        c_p95 = float(c['p95'])
        b_err = float(b['error_rate'])
        c_err = float(c['error_rate'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metric values: {e}")

    # Percentual de melhoria (positivo significa candidate pior se usarmos (b-c)/b*100)
    delta_p95 = (b_p95 - c_p95) / b_p95 * 100 if b_p95 != 0 else 0.0
    delta_error = (c_err - b_err)

    explanation = []

    # Decisão baseada em thresholds configuráveis
    if delta_p95 > P95_IMPROVEMENT_AUTO and delta_error <= ERROR_RATE_INCREASE_TOLERANCE:
        decision = 'approve_auto'
        explanation.append(f'p95 improved by {delta_p95:.2f}% (>{P95_IMPROVEMENT_AUTO}%) and error rate not increased beyond tolerance')
    elif delta_p95 > P95_IMPROVEMENT_MANUAL:
        decision = 'manual_review'
        explanation.append(f'p95 improved by {delta_p95:.2f}% (>{P95_IMPROVEMENT_MANUAL}%) but requires manual check')
        if delta_error > ERROR_RATE_INCREASE_TOLERANCE:
            explanation.append(f'error rate increased by {delta_error:.4f} (> tolerance {ERROR_RATE_INCREASE_TOLERANCE})')
    else:
        decision = 'reject'
        explanation.append(f'p95 not improved (delta {delta_p95:.2f}%)')
        if delta_error > ERROR_RATE_INCREASE_TOLERANCE:
            explanation.append(f'error rate increased by {delta_error:.4f} (> tolerance {ERROR_RATE_INCREASE_TOLERANCE})')

    result = {
        'decision': decision,
        'delta_p95_percent': round(delta_p95, 3),
        'delta_error_absolute': round(delta_error, 6),
        'thresholds': {
            'p95_improvement_auto': P95_IMPROVEMENT_AUTO,
            'p95_improvement_manual': P95_IMPROVEMENT_MANUAL,
            'error_rate_increase_tolerance': ERROR_RATE_INCREASE_TOLERANCE
        },
        'explanation': explanation,
        'baseline': {'p95': b_p95, 'error_rate': b_err},
        'candidate': {'p95': c_p95, 'error_rate': c_err}
    }

    return result
