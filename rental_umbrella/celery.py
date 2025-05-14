from celery import Celery

# 時間設定用
app = Celery('umbrellas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
