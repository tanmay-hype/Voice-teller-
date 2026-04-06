import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("worker", broker=broker_url, backend=result_backend)
celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.task_routes = {
    "worker.tasks.generate_tts_task": "main-queue"
}

# Auto-discover tasks in all modules
celery_app.autodiscover_tasks(["worker.tasks"])
