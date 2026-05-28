#!/bin/bash
set -e
 
# Wait until PostgreSQL is ready (retry every second):
echo 'Waiting for PostgreSQL...'
while ! python -c "import psycopg2; psycopg2.connect(...)" 2>/dev/null; do
    sleep 1
done
echo 'PostgreSQL is ready.'
 
# Run all pending migrations automatically:
python manage.py migrate --noinput
 
# Register the daily Celery Beat task in the database:
python manage.py shell -c "	
from django_celery_beat.models import PeriodicTask, CrontabSchedule
schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='0', hour='6',   # 6:00 AM UTC = 11:30 AM IST
    day_of_week='*', day_of_month='*', month_of_year='*',
)
PeriodicTask.objects.get_or_create(
    crontab=schedule,
    name='Daily Flight Price Check',
    defaults={'task': 'scheduler.tasks.check_all_routes'},
)"
 
exec "$@"   # run whatever command Docker passes next (gunicorn)
