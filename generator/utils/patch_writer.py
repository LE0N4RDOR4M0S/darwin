import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("patch")

class PatchWriter:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.output_dir = os.path.join(repo_path, "patches")
        os.makedirs(self.output_dir, exist_ok=True)

    def write_patch(self, file_path: str, new_content: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patch_file = os.path.join(self.output_dir, f"patch_{timestamp}.java")

        with open(patch_file, "w") as f:
            f.write(new_content)

        logger.info(f"🧩 Patch salvo: {patch_file}")
        return patch_file
