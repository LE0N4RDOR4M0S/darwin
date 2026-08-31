import os
from datetime import datetime
from fastapi import FastAPI, Response, HTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from models import GenerationRequest, PatchResult, HotspotType
from utils.git_helper import GitHelper
from utils.ast_parser import ASTParser
from utils.patch_writer import PatchWriter
from utils.logger import get_logger

from heuristics.timeout_rule import apply_timeout_rule
from heuristics.pool_size_rule import apply_pool_size_rule
from heuristics.caching_rule import apply_caching_rule

app = FastAPI(title="Código Vivo - Patch Generator", version="1.0.0")
logger = get_logger("generator")

REPO_PATH = os.getenv("REPO_PATH", "/repo")
git = GitHelper(repo_path=REPO_PATH)
parser = ASTParser(repo_path=REPO_PATH)
patch_writer = PatchWriter(repo_path=REPO_PATH)


def select_rule_for_hotspot(hotspot_type: HotspotType):
    """
    Mapeamento determinístico entre tipo de hotspot e regra de heurística.
    - latency    → caching (primeira opção) ou timeout
    - cpu_usage  → pool_size
    - error_rate → timeout
    """
    if hotspot_type == HotspotType.LATENCY:
        return "caching", apply_caching_rule
    elif hotspot_type == HotspotType.CPU_USAGE:
        return "pool_size", apply_pool_size_rule
    elif hotspot_type == HotspotType.ERROR_RATE:
        return "timeout", apply_timeout_rule
    return "timeout", apply_timeout_rule


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "generator",
        "repo_path": REPO_PATH,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/generate", response_model=PatchResult)
async def generate_patch(payload: GenerationRequest):
    """
    Gera um patch de código candidato com base em um hotspot recebido.
    1. Identifica o hotspot principal.
    2. Seleciona a heurística apropriada.
    3. Localiza o arquivo Java correspondente via ASTParser.
    4. Aplica a heurística e salva o patch via PatchWriter.
    5. Cria um branch git candidato.
    """
    logger.info(f"🧠 Solicitação de geração recebida: {len(payload.hotspots)} hotspot(s)")

    if not payload.hotspots:
        raise HTTPException(status_code=400, detail="Nenhum hotspot fornecido no payload.")

    hotspot = payload.hotspots[0]
    rule_name, rule_fn = select_rule_for_hotspot(hotspot.type)
    logger.info(f"🎯 Hotspot: type={hotspot.type} endpoint={hotspot.endpoint} → Regra: {rule_name}")

    file_path = parser.find_relevant_file(hotspot.model_dump())
    if not file_path:
        # Se não encontrar arquivo Java específico, tenta um fallback inteligente
        file_path = os.path.join(REPO_PATH, "src/main/java/com/example/codigovivo/controller/SampleController.java")
        if not os.path.exists(file_path):
            # Em ambiente isolado sem repo clonado, cria arquivo dummy para teste
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write('package com.example.codigovivo.controller;\n\npublic class SampleController {\n    public String getData() {\n        return "data";\n    }\n}\n')

    try:
        modified_code = rule_fn(file_path)
        patch_file = patch_writer.write_patch(file_path, modified_code)
        branch_name = git.create_candidate_branch(patch_file, rule=rule_name)

        logger.info(f"✅ Candidate branch criado com sucesso: {branch_name}")
        return PatchResult(
            status="success",
            branch=branch_name,
            file_path=patch_file,
            rule_applied=rule_name,
            message="Patch gerado e commitado em candidate branch com sucesso.",
        )
    except Exception as e:
        logger.error(f"❌ Falha ao aplicar heurística {rule_name}: {e}")
        return PatchResult(
            status="error",
            rule_applied=rule_name,
            message=str(e),
        )


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
