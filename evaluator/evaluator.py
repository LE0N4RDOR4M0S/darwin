from fastapi import FastAPI, UploadFile, File, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics.scoring import evaluate_metrics
from utils.report_builder import build_report
from utils.logger import get_logger
from datetime import datetime
import json
import tempfile

app = FastAPI(title="Código Vivo Evaluator", version="1.0.0")
logger = get_logger("evaluator")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "evaluator"
    }


@app.post("/evaluate")
async def evaluate_patch(baseline: dict, candidate: dict):
    """Evaluate a patch by comparing baseline vs candidate metrics"""
    try:
        logger.info("Starting patch evaluation")
        
        # Calcula score
        score = evaluate_metrics(baseline, candidate)
        
        # Decide recomendação
        if score >= 0.85:
            recommendation = "approve_auto"
        elif score >= 0.5:
            recommendation = "review_manual"
        else:
            recommendation = "reject"
        
        # Build report
        report = build_report(baseline, candidate, score, recommendation)
        
        logger.info(f"Evaluation complete. Score: {score}, Recommendation: {recommendation}")
        
        return {
            "score": score,
            "recommendation": recommendation,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error evaluating patch: {e}")
        return {"status": "error", "message": str(e)}


@app.get('/metrics')
async def metrics():
    """Prometheus metrics"""
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.post("/evaluate")
async def evaluate(baseline: UploadFile = File(...), candidate: UploadFile = File(...)):
    """
    Recebe dois arquivos JSON (baseline e candidate),
    calcula deltas de métricas e define uma decisão automatizada.
    """
    try:
        baseline_data = json.load(baseline.file)
        candidate_data = json.load(candidate.file)

        result = evaluate_metrics(baseline_data, candidate_data)
        report = build_report(result)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            json.dump(report, tmp, indent=2)
            logger.info(f"📊 Relatório gerado: {tmp.name}")

        return report

    except Exception as e:
        logger.error(f"❌ Erro durante avaliação: {e}")
        return {"status": "error", "message": str(e)}
