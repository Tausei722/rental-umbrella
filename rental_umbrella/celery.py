from celery import Celery
from celery.schedules import crontab

# 時間設定用
app = Celery('umbrellas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


CELERY_BEAT_SCHEDULE = {
    'run_task_every_12_hours': {
        'task': 'your_app.tasks.check_reservation_status',  # 実行するタスク
        'schedule': crontab(minute=0, hour='*/12'),  # 🔥 12時間ごとに実行
    },
}