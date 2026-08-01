# ============================================================
# FlightPulse backend image — shared by web, worker, and beat.
# No apt packages needed: psycopg2-binary ships as a wheel, and the
# Postgres readiness wait in entrypoint.sh is pure Python.
# ============================================================
FROM python:3.12-slim

# Faster, cleaner Python in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps first so this layer caches across code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
# Default command (overridden by worker/beat services in docker-compose)
CMD ["gunicorn", "flightpulse.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
