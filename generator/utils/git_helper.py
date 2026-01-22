import os
import subprocess
from utils.logger import get_logger

logger = get_logger("git")

class GitHelper:
    def __init__(self, repo_path="/repo"):
        self.repo_path = repo_path
        os.makedirs(repo_path, exist_ok=True)

    def create_candidate_branch(self, patch_path: str) -> str:
        branch_name = f"candidate_{os.path.basename(patch_path).split('.')[0]}"
        subprocess.run(["git", "-C", self.repo_path, "checkout", "-b", branch_name])
        subprocess.run(["git", "-C", self.repo_path, "add", "."])
        subprocess.run(["git", "-C", self.repo_path, "commit", "-m", f"Auto patch {branch_name}"])
        logger.info(f"🪶 Branch criado: {branch_name}")
        return branch_name
