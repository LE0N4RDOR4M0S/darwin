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
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get('/metrics')
async def metrics():
    data = generate_latest()
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
