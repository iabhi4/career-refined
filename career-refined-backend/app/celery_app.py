import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

celery_app = Celery(
    "latex_tasks",
    broker="amqp://guest:guest@localhost:5672//",  # RabbitMQ default URL
    backend="rpc://",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
)

# The rest of your imports or Celery tasks
import app.services.latex