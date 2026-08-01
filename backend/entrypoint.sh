#!/bin/bash
set -e

# Wait until PostgreSQL accepts connections (pure Python — no apt packages needed):
echo 'Waiting for PostgreSQL...'
python <<'PY'
import os, time
import psycopg2
while True:
    try:
        psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            host=os.getenv('DB_HOST', 'db'),
            port=os.getenv('DB_PORT', '5432'),
        ).close()
        break
    except Exception:
        time.sleep(1)
PY
echo 'PostgreSQL is ready.'

# Only the web container runs migrations / static collection / schedule registration,
# so the worker and beat containers don't race against it on startup.
if [ "${RUN_MIGRATIONS}" = "true" ]; then
    echo 'Applying migrations...'
    python manage.py migrate --noinput

    echo 'Collecting static files...'
    python manage.py collectstatic --noinput

    echo 'Registering daily Celery Beat task...'
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
fi

exec "$@"   # run whatever command Docker passes next (gunicorn / celery)
