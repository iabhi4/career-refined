from celery import Celery

celery_app = Celery(
    "latex_tasks",
    broker="amqp://guest:guest@localhost:5672//",  # RabbitMQ default URL; adjust if needed
    backend="rpc://",  # or consider Redis as result backend if desired
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,  # tasks expire in one hour
)