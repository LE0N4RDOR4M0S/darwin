import httpx
from utils.logger import get_logger

logger = get_logger("api_client")

class GeneratorClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def generate_candidate(self, hotspot_data: dict):
        url = f"{self.base_url}/generate"
        logger.info(f"📨 Enviando hotspot ao Generator: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=hotspot_data)
            response.raise_for_status()
            return response.json()

class EvaluatorClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def evaluate_candidate(self, candidate: dict):
        url = f"{self.base_url}/evaluate"
        logger.info(f"🧠 Enviando candidato ao Evaluator: {url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=candidate)
            response.raise_for_status()
            return response.json()
