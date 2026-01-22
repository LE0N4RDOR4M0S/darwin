from utils.logger import get_logger
from datetime import datetime
import json
import os

logger = get_logger("scheduler")

class JobScheduler:
    def __init__(self, storage_dir="jobs_log"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def log_job_result(self, candidate: dict, evaluation: dict, decision: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.storage_dir, f"job_{timestamp}.json")
        record = {
            "timestamp": timestamp,
            "candidate": candidate,
            "evaluation": evaluation,
            "decision": decision
        }
        with open(filename, "w") as f:
            json.dump(record, f, indent=2)
        logger.info(f"📦 Resultado registrado: {filename}")
