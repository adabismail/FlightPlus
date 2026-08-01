# FlightPulse

A real-time flight **deal tracker** that alerts users when fares between selected
cities drop below a target price — a lightweight "Skyscanner + Notify."

Users register routes (FROM → TO + max budget). A scheduled job fetches live fares
from the **Sky-Scrapper API (RapidAPI)** every day, compares them against each user's
threshold, and when a deal is found it stores an alert and notifies the user by
**email and/or SMS**. Signups are confirmed with an emailed **OTP code**.

---

## Architecture

Containerized into **5 services behind an Nginx proxy**:

```
                         ┌─────────────┐
   browser  ──────────▶  │    nginx    │  serves React build, proxies /api, /admin
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐        ┌──────────────┐
                         │     web     │◀──────▶│      db      │  PostgreSQL
                         │ Django+gunicorn      │  (Postgres)  │
                         └──────┬──────┘        └──────▲───────┘
                                │                      │
              enqueue jobs ┌────▼────┐  results        │
                           │  redis  │◀────────────────┤
                           └────┬────┘                 │
                    ┌───────────┴───────────┐          │
              ┌─────▼─────┐           ┌──────▼──────┐   │
              │  worker   │           │    beat     │   │
              │ (Celery)  │           │ (scheduler) │───┘
              └───────────┘           └─────────────┘
```

**ETL pipeline:** `beat` fires daily → `check_all_routes` **fans out one Celery task
per active route** → each `check_single_route` task fetches live offers from Sky-Scrapper
(**extract**), normalizes them and compares to the threshold (**transform**), and
persists + delivers an alert (**load**).

---

## Tech stack

| Layer        | Technology                                              |
|--------------|---------------------------------------------------------|
| Backend      | Django 5, Django REST Framework                          |
| Auth         | JWT (SimpleJWT) + email OTP verification on signup       |
| Database     | PostgreSQL                                               |
| Async / ETL  | Celery + Redis (worker) and Celery Beat (scheduler)      |
| Flight data  | Sky-Scrapper API via RapidAPI (real fares + details)     |
| Alerting     | SMTP (email) + Twilio (SMS)                              |
| Frontend     | React + Vite (hand-built dark "control room" UI)         |
| Infra        | Docker Compose (5 services) + Nginx + Gunicorn          |

---

## Quick start (Docker)

```bash
cp .env.example .env        # then fill in API keys (see below)
docker compose up --build   # builds and starts all 6 containers
```

Then open:

- **App:** http://localhost/
- **Django admin:** http://localhost/admin/  (create a superuser first, below)

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

### Local dev (without Docker)

```bash
# backend
cd backend && pip install -r requirements.txt
python manage.py migrate && python manage.py runserver
# in separate shells:
celery -A flightpulse worker -l info
celery -A flightpulse beat   -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# frontend
cd frontend && npm install && npm run dev   # http://localhost:5173 (proxies /api → :8000)
```

---

## API keys / configuration

All secrets are read from `.env` (copy from `.env.example`). **The app runs fully
without them** — the stack boots, every screen works, and emails fall back to the
console backend. You only need keys for live data and real delivery:

| Variable | Purpose | Where it's used |
|----------|---------|-----------------|
| `RAPIDAPI_KEY` | Live flight search + prices (Sky-Scrapper) | `backend/services/flight_service.py` (via `settings.py`) |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | SMS alerts | `backend/services/alerting_service.py` (via `settings.py`) |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (+ `EMAIL_HOST`) | Email alerts | `backend/services/alerting_service.py` (via `settings.py`) |
| `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` | Django core | `backend/flightpulse/settings.py` |
| `DB_*`, `CELERY_BROKER_URL` | Postgres + Redis | `backend/flightpulse/settings.py` |

Every key is consumed in `backend/flightpulse/settings.py`, marked with
`>>> API KEYS REQUIRED HERE <<<`.

---

## REST API

Base path: `/api/` (JWT `Authorization: Bearer <access>` on everything except
register/login/refresh).

| Method(s) | Endpoint | Description |
|-----------|----------|-------------|
| POST | `/api/auth/register/` | Create account (inactive), email a verification OTP |
| POST | `/api/auth/verify-otp/` | Confirm the OTP → activate account, return tokens |
| POST | `/api/auth/resend-otp/` | Re-send a verification code |
| POST | `/api/auth/login/` | Obtain tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Blacklist refresh token |
| GET / PUT / PATCH | `/api/auth/me/` | Current user profile |
| GET / POST | `/api/routes/` | List / create tracked routes |
| GET / PUT / PATCH / DELETE | `/api/routes/{id}/` | Retrieve / update / delete a route |
| POST | `/api/routes/{id}/pause/` | Pause tracking |
| POST | `/api/routes/{id}/resume/` | Resume tracking |
| POST | `/api/routes/{id}/check_now/` | Queue an on-demand price check |
| GET | `/api/routes/stats/` | Dashboard counters |
| GET | `/api/alerts/` | Alert history (filter: `?route=&airline_code=&channel=&is_delivered=`) |
| GET | `/api/alerts/{id}/` | Retrieve an alert |

---

## Project layout

```
backend/
  flightpulse/      # settings, celery app, root urls
  users/            # custom email user + JWT auth
  routes/           # TrackedRoute model, viewset, serializers
  alerts/           # Alert model (history), read-only API with filters
  services/         # flight_service · price_checker · alerting_service (the ETL)
  schedular/        # Celery tasks (fan-out scheduler)
frontend/
  src/pages/        # Login, Register, Dashboard, Alerts, Settings
  src/components/    # Navbar, StatsBar, RouteCard, AlertCard, AddRouteModal
  src/services/api.js   # axios client w/ JWT refresh
docker-compose.yml  # db · redis · web · worker · beat · nginx
```
