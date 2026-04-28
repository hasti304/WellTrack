# Welltrack

Welltrack is a wellness web app: profile and goals, food and exercise logging, an AI **Smart Coach** with optional RAG grounding, and **7-day plans** with goal-match scoring and PDF export.

**Live app:** replace with your URL, e.g. `https://welltrack-lztn.onrender.com`

---

## Problem

People track fitness and nutrition in scattered notes and apps. Welltrack centralizes **profile metrics** (BMI, Navy body-fat estimate), **logs** (meals, workouts), **guided coaching** (with citations when RAG is enabled), and **weekly plans** scored against stated goals.

---

## Stack

| Layer | Technology |
|--------|------------|
| Backend | Django 5.1, Gunicorn (production) |
| Auth | Django users, optional Google OAuth (`social-auth-app-django`) |
| Database | SQLite locally; PostgreSQL / **Supabase** in production via `DATABASE_URL` |
| LLM | OpenAI-compatible API (`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`) |
| RAG (optional) | Chroma + local embeddings (`chromadb`, `sentence-transformers`) — heavy; often **disabled on Render** with `RAG_ENABLED=False` and slim `requirements-production.txt` |
| Frontend | Django templates + Bootstrap; some pages use client JS (e.g. Smart Coach, 7-day plan) |

---

## Local setup

1. **Clone and venv**

   ```bash
   git clone https://github.com/YOUR_ORG/WellTrack.git
   cd WellTrack
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Environment**

   ```bash
   copy .env.example .env
   ```

   Fill at least `SECRET_KEY`, LLM variables if you use coach/plan generation. Leave `DATABASE_URL` empty for **SQLite**.

3. **Migrate and run**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser   # optional
   python manage.py runserver
   ```

4. **RAG ingest (optional, full `requirements.txt` only)**

   ```bash
   python manage.py ingest_rag_sources
   ```

---

## Production (Render + Supabase)

1. **Supabase:** create a project; use the **transaction pooler** `DATABASE_URL` (port `6543`, `*.pooler.supabase.com`, `sslmode=require`) if direct `db.*.supabase.co` fails from Render (IPv6 / network issues).

2. **Render:** Web Service, Python from repo **`runtime.txt`** (3.12.x).

   - **Build:** `pip install -r requirements-production.txt && python manage.py collectstatic --noinput`  
     (or full `requirements.txt` if you need RAG on the server and accept large installs + persistent disk for Chroma.)

   - **Start:** `python manage.py migrate && gunicorn welltrack.wsgi:application --bind 0.0.0.0:$PORT`

3. **Environment variables** (minimum): `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, LLM keys. Optional: `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`, `RAG_ENABLED=False` for slim deploys.

See **`.env.example`** for names and comments.

---

## Health check (uptime monitors)

Point **GET** `/health/` at your base URL, e.g. `https://YOUR-SERVICE.onrender.com/health/`

Returns JSON: `{"status": "ok", "service": "welltrack"}` (no database query).

---

## Smoke test (production)

After deploy:

1. Open `/` and `/health/`
2. Register → login
3. Profile: save goals / optional numeric targets
4. Dashboard: quick-add food, open exercises and log one
5. Smart Coach: send a message; if RAG on, check citations
6. 7-day plan: generate → goal match → save → PDF

---

## Screenshots (for reviewers / README)

Add images to your repo or docs and link them here:

- Dashboard with real logs  
- Smart Coach answer with a citation (when RAG enabled)  
- 7-day plan with goal-match score  

---

## License

Add your license (e.g. MIT) if you open-source the project.
