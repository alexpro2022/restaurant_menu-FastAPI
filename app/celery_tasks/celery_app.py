from celery import Celery
from app.celery_tasks import celeryconfig


app = Celery(include=['app.celery_tasks.tasks'])
app.config_from_object(celeryconfig)
