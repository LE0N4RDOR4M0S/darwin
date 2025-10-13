from fastapi import FastAPI, BackgroundTasks, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from utils.api_client import GeneratorClient, EvaluatorClient
from utils.job_scheduler import JobScheduler
from utils.logger import get_logger
from datetime import datetime

app = FastAPI(title="Código Vivo Orchestrator", version="1.0.0")
logger = get_logger("orchestrator")

scheduler = JobScheduler()
generator = GeneratorClient(base_url="http://generator:5002/generate")
evaluator = EvaluatorClient(base_url="http://evaluator:5001")

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get('/metrics')
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.post("/hotspot")
async def receive_hotspot(data: dict, background_tasks: BackgroundTasks):
    """
    Endpoint chamado pelo Detector quando um hotspot é identificado.
    Inicia o processo de geração, teste e avaliação de candidato.
    """
    logger.info(f"🔥 Hotspot recebido: {data}")
    background_tasks.add_task(handle_hotspot, data)
    return {"status": "accepted", "received_at": datetime.now().isoformat()}

async def handle_hotspot(data: dict):
    """
    Função de orquestração principal:
    1. Aciona o generator → cria branch candidato
    2. Aguarda build/testes → envia pro evaluator
    3. Interpreta o resultado e decide deploy
    """
    try:
        candidate = await generator.generate_candidate(data)
        logger.info(f"🧩 Candidato gerado: {candidate.get('branch')}")

        evaluation = await evaluator.evaluate_candidate(candidate)
        logger.info(f"📊 Avaliação concluída: {evaluation}")

        decision = evaluation.get("decision", "manual_review")
        logger.info(f"🤖 Decisão final: {decision}")

        scheduler.log_job_result(candidate, evaluation, decision)

    except Exception as e:
        logger.error(f"❌ Falha no ciclo de orquestração: {e}")
