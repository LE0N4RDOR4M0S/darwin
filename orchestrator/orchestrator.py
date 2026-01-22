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
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "orchestrator"
    }


@app.post("/hotspots")
async def process_hotspot(hotspot: dict, background_tasks: BackgroundTasks):
    """Process a hotspot by generating and evaluating patches"""
    try:
        logger.info(f"Processing hotspot: {hotspot}")
        
        # Schedule background job
        background_tasks.add_task(handle_hotspot, hotspot)
        
        return {
            "status": "queued",
            "hotspot_id": hotspot.get("id", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing hotspot: {e}")
        return {"status": "error", "message": str(e)}


async def handle_hotspot(hotspot: dict):
    """Background task to handle hotspot processing"""
    try:
        logger.info(f"Starting hotspot handling: {hotspot}")
        
        # Step 1: Generate patch
        logger.info("Calling generator...")
        patch_response = await generator.generate(hotspot)
        
        # Step 2: Evaluate patch
        logger.info("Calling evaluator...")
        eval_response = await evaluator.evaluate(patch_response)
        
        # Step 3: Make decision
        recommendation = eval_response.get("recommendation", "reject")
        
        if recommendation == "approve_auto":
            logger.info(f"Auto-approving patch for hotspot {hotspot.get('id')}")
            # TODO: Deploy patch
        elif recommendation == "review_manual":
            logger.info(f"Patch requires manual review for hotspot {hotspot.get('id')}")
            # TODO: Notify team
        else:
            logger.info(f"Rejecting patch for hotspot {hotspot.get('id')}")
        
        logger.info(f"Hotspot handling complete: {hotspot.get('id')}")
        
    except Exception as e:
        logger.error(f"Error handling hotspot: {e}")


@app.get('/metrics')
async def metrics():
    """Prometheus metrics"""
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
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
