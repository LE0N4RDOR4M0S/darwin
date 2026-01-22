from fastapi import FastAPI, BackgroundTasks, Response
from utils.git_helper import GitHelper
from utils.ast_parser import ASTParser
from utils.patch_writer import PatchWriter
from heuristics.timeout_rule import apply_timeout_rule
from heuristics.pool_size_rule import apply_pool_size_rule
from heuristics.caching_rule import apply_caching_rule
from utils.logger import get_logger
import random
import os
from datetime import datetime
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Código Vivo Generator", version="1.0.0")
logger = get_logger("generator")

git = GitHelper(repo_path=os.getenv("REPO_PATH", "/repo"))
parser = ASTParser(repo_path=git.repo_path)
patch_writer = PatchWriter(repo_path=git.repo_path)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "generator"
    }


@app.post("/generate")
async def generate_patch(hotspot: dict, background_tasks: BackgroundTasks):
    """Generate a patch for a detected hotspot"""
    try:
        logger.info(f"Generating patch for hotspot: {hotspot}")
        
        # Seleciona heurística aleatória
        heuristics = [
            apply_timeout_rule,
            apply_pool_size_rule,
            apply_caching_rule
        ]
        heuristic = random.choice(heuristics)
        
        # Aplicar heurística
        patch = heuristic(hotspot)
        
        logger.info(f"Patch generated: {patch}")
        return {
            "status": "success",
            "patch": patch,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating patch: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)

@app.get("/health")
async def health():
    return {"status": "ok", "repo": git.repo_path, "time": datetime.now().isoformat()}


@app.get('/metrics')
async def metrics():
    # minimal Prometheus metrics endpoint
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.post("/generate")
async def generate_candidate(data: dict, background_tasks: BackgroundTasks):
    """
    Gera um novo branch candidato com base em heurísticas simples.
    """
    logger.info(f"🧠 Hotspot recebido para geração: {data}")
    background_tasks.add_task(handle_generation, data)
    return {"status": "accepted", "started_at": datetime.now().isoformat()}

async def handle_generation(data: dict):
    try:
        hotspot = data.get("hotspots", [{}])[0]
        rule = random.choice(["timeout", "pool_size", "cache"])
        logger.info(f"🎯 Regra selecionada: {rule}")

        file_path = parser.find_relevant_file(hotspot)
        if not file_path:
            logger.warning("Nenhum arquivo correspondente encontrado.")
            return

        if rule == "timeout":
            modified_code = apply_timeout_rule(file_path)
        elif rule == "pool_size":
            modified_code = apply_pool_size_rule(file_path)
        else:
            modified_code = apply_caching_rule(file_path)

        patch_path = patch_writer.write_patch(file_path, modified_code)
        branch_name = git.create_candidate_branch(patch_path)

        logger.info(f"✅ Candidato criado: {branch_name}")
        return {"branch": branch_name, "file": file_path, "rule": rule}

    except Exception as e:
        logger.error(f"❌ Falha na geração de candidato: {e}")
