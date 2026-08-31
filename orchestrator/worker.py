"""
Celery application para o Darwin Orchestrator.
Broker e backend: Redis.
Iniciar o worker com:
    celery -A worker worker --loglevel=info
"""
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "darwin_orchestrator",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"],  # módulo onde as tasks estão definidas
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,          # acknowledge só após conclusão (at-least-once)
    worker_prefetch_multiplier=1, # um job por worker (evita acúmulo em memória)
    task_soft_time_limit=300,     # 5 min soft limit
    task_time_limit=360,          # 6 min hard limit
)
