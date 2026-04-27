Welltrack — setup
==================

1) Create and activate a virtual environment, then install dependencies:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2) Copy environment file:

   copy .env.example .env

  Edit .env: set SECRET_KEY, DEBUG, and optional keys (LLM_* / OPENAI_API_KEY for AI,
  UNSPLASH_ACCESS_KEY, GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET). For PostgreSQL in
  production, prefer DATABASE_URL. Legacy DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT
  is still supported. If neither is set, SQLite is used.

3) Apply migrations and create an admin user:

   python manage.py migrate
   python manage.py createsuperuser

4) Optional: seed exercises (bulk insert; re-running may duplicate names unless you clear exercises first):

   python seed_exercises.py

5) Run the development server:

   python manage.py runserver

6) Optional: ingest Smart Coach RAG snippets (local embeddings + Chroma):

   python manage.py ingest_rag_sources --file data/rag/sources.jsonl

6) Google OAuth: in Google Cloud Console, add authorized redirect URIs such as:

   http://127.0.0.1:8000/auth/complete/google-oauth2/

   Use the same origin you browse with (127.0.0.1 vs localhost) so the redirect matches.

Notes
-----
- JSON POST endpoints (/api/chatbot/, /api/smart-coach/, seven-day plan APIs) require a
  valid CSRF token (X-CSRFToken header + session cookie), same as normal form POSTs.
- Production: DEBUG=False, explicit ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS behind HTTPS, secure SECRET_KEY.

Secrets — when you need to paste keys (read this before filling .env)
-----------------------------------------------------------------------
The app will ASK you to add keys only when you turn on a feature that needs
them. Nothing below is required for a basic local run (SQLite, no login with
Google, no AI, no Unsplash hero). Put real values only in .env on your
machine; never commit .env or paste keys into chat logs unless you trust the
channel and plan to rotate the key afterward.

SECRET_KEY
  What: Django’s cryptographic signing key (sessions, CSRF tokens, password
  reset links, etc.).
  When you need it: Before any serious local use or deployment. Generate a
  long random string; keep it private.
  Where: Only in .env as SECRET_KEY=...

DEBUG / ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS
  What: Control error reporting, which hosts can serve the site, and which
  origins are trusted for CSRF when using HTTPS.
  When: Production deploys need DEBUG=False, explicit ALLOWED_HOSTS, and
  CSRF_TRUSTED_ORIGINS for your real domain (e.g. https://app.example.com).

PostgreSQL (DATABASE_URL or DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT)
  What: Database connection. DATABASE_URL is Render-native and takes priority.
  If DATABASE_URL is empty, legacy DB_* values are used. If DB_NAME is also empty,
  the project uses SQLite and you do not need database passwords.
  When: Use DATABASE_URL for production deploys (Render), DB_* for local/manual setups.

LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_API_BASE (and legacy OPENAI_API_KEY)
  What: Chatbot, Smart Coach, and 7-day plan use one OpenAI-compatible HTTP API
  (legacy openai Python package: ChatCompletion + configurable api_base).

  Set LLM_PROVIDER to one of:
    - openai       — https://api.openai.com/v1  (default model gpt-3.5-turbo)
    - openrouter   — https://openrouter.ai/api/v1  (default model openai/gpt-3.5-turbo)
    - sambanova    — https://api.sambanova.ai/v1  (you MUST set LLM_MODEL from
                     SambaNova Cloud → APIs: https://cloud.sambanova.ai/apis )
    - cerebras     — https://api.cerebras.ai/v1  (you MUST set LLM_MODEL from
                     Cerebras inference docs / dashboard: https://www.cerebras.ai/ )

  Keys: Put the provider’s API key in LLM_API_KEY=...  If LLM_API_KEY is empty,
  OPENAI_API_KEY is still read for backward compatibility.

  Models: For OpenRouter, use their slugs (e.g. openai/gpt-3.5-turbo or any model
  listed on openrouter.ai). For SambaNova and Cerebras, copy the exact model id
  your account exposes into LLM_MODEL=...

  Optional LLM_API_BASE= overrides the default base URL (e.g. if SambaNova shows
  a tenant-specific endpoint in the portal).

  Billing / limits: Each vendor has its own pricing and rate limits; check their
  dashboards after you create a key.

RAG_ENABLED, RAG_TOP_K, RAG_PERSIST_DIR, RAG_COLLECTION, RAG_EMBEDDING_MODEL
  What: Smart Coach retrieval-augmented context grounded in curated wellness snippets.
  Defaults use local sentence-transformers embeddings and Chroma persistence.
  When: Enable by default for cited Smart Coach answers. Re-ingest snippets whenever
  your source corpus changes:
    python manage.py ingest_rag_sources --file data/rag/sources.jsonl

UNSPLASH_ACCESS_KEY
  What: Unsplash “Client Access Key” for their API so the home page can fetch
  a random “health” photo for the hero image.
  When: Only if you want that hero image. Register an app at Unsplash
  Developers, copy the Access Key into .env as UNSPLASH_ACCESS_KEY=...
  Without it: Home still works; the template shows a placeholder message.

GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
  What: OAuth 2.0 credentials for “Sign in with Google” (social-auth-app-django).
  When: Only when you want Google login. Create an OAuth client of type
  “Web application” in Google Cloud Console, set authorized redirect URIs to
  match your site (e.g. http://127.0.0.1:8000/auth/complete/google-oauth2/ for
  local dev). Put Client ID and Client Secret in .env.
  Without them: Username/password login still works; the Google button may fail
  if clicked without valid credentials.

Workflow for future changes
----------------------------
If a task requires a new key, you will be told explicitly which variable name,
what it unlocks, where to obtain it, and to add it to .env before testing —
before assuming the feature works.
