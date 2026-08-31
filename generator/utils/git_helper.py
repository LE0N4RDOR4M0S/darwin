import os
import subprocess
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("git")


class GitHelper:
    def __init__(self, repo_path: str = "/repo"):
        self.repo_path = repo_path
        os.makedirs(repo_path, exist_ok=True)
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        git_dir = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_dir):
            try:
                subprocess.run(["git", "-C", self.repo_path, "init"], check=True, capture_output=True)
                # Configurar user dummy se não houver
                subprocess.run(["git", "-C", self.repo_path, "config", "user.name", "Darwin Bot"], check=False)
                subprocess.run(["git", "-C", self.repo_path, "config", "user.email", "bot@darwin.ai"], check=False)
                logger.info(f"🌱 Repositório git inicializado em: {self.repo_path}")
            except Exception as e:
                logger.error(f"❌ Falha ao inicializar repo git: {e}")

    def create_candidate_branch(self, patch_path: str, rule: str = "patch") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"darwin/{rule}_{timestamp}"

        try:
            subprocess.run(["git", "-C", self.repo_path, "checkout", "-b", branch_name], check=True, capture_output=True)
            subprocess.run(["git", "-C", self.repo_path, "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "-C", self.repo_path, "commit", "-m", f"Darwin Auto Patch ({rule}): {os.path.basename(patch_path)}"], check=True, capture_output=True)
            logger.info(f"🪶 Branch candidato criado: {branch_name}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao criar branch git (prosseguindo em modo simulado): {e}")

        return branch_name
