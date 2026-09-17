from celery import Celery
from app.shared.config import config


app = Celery(
    'myapp',
    broker=f'redis://:{config.redis.password.get_secret_value()}@{config.redis.host}:{config.redis.port}/3',
    backend=f'redis://:{config.redis.password.get_secret_value()}@{config.redis.host}:{config.redis.port}/3',
    include=[
        'app.business_logic.celery_tasks.sender_tasks',
    ],
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Moscow',
    enable_utc=True,
)