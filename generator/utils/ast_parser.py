import os
from utils.logger import get_logger

logger = get_logger("ast")

class ASTParser:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def find_relevant_file(self, hotspot: dict) -> str:
        """
        Localiza arquivo Java provável com base no endpoint informado.
        Exemplo: se hotspot endpoint = /api/user, busca UserController.java
        """
        keyword = hotspot.get("endpoint", "unknown").split("/")[-1].capitalize()
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if keyword in f and f.endswith(".java"):
                    path = os.path.join(root, f)
                    logger.info(f"🔍 Arquivo relevante encontrado: {path}")
                    return path
        return None
