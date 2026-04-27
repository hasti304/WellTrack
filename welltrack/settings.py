"""
Django settings for Welltrack.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me-in-production")

DEBUG = env.bool("DEBUG", default=True)

_allowed = env("ALLOWED_HOSTS", default="")
if DEBUG and not _allowed.strip():
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]

_csrf = env("CSRF_TRUSTED_ORIGINS", default="")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "social_django",
    "widget_tweaks",
    "accounts.apps.AccountsConfig",
    "fitness.apps.FitnessConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "welltrack.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "welltrack.wsgi.application"

_db_name = env("DB_NAME", default="")
_database_url = env("DATABASE_URL", default="")
if _database_url:
    DATABASES = {
        "default": env.db("DATABASE_URL"),
    }
elif _db_name:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER", default="postgres"),
            "PASSWORD": env("DB_PASSWORD", default=""),
            "HOST": env("DB_HOST", default="localhost"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_CLIENT_ID", default="")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_CLIENT_SECRET", default="")
GOOGLE_OAUTH_ENABLED = bool(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY.strip() and SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET.strip()
)

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
# OpenAI-compatible LLM: openai | openrouter | sambanova | cerebras
LLM_PROVIDER = env("LLM_PROVIDER", default="openai").lower().strip()
_llm_api_key = env("LLM_API_KEY", default="")
LLM_API_KEY = _llm_api_key.strip() if _llm_api_key.strip() else OPENAI_API_KEY
LLM_MODEL = env("LLM_MODEL", default="")
LLM_API_BASE = env("LLM_API_BASE", default="")

RAG_ENABLED = env.bool("RAG_ENABLED", default=True)
RAG_TOP_K = env.int("RAG_TOP_K", default=4)
RAG_PERSIST_DIR = env("RAG_PERSIST_DIR", default=str(BASE_DIR / "chroma_db"))
RAG_COLLECTION = env("RAG_COLLECTION", default="welltrack_guidelines")
RAG_EMBEDDING_MODEL = env(
    "RAG_EMBEDDING_MODEL", default="sentence-transformers/all-MiniLM-L6-v2"
)

# Smart Coach: recent chat turns sent to the LLM (excluding the new user message count adjustment in code).
SMART_COACH_MAX_HISTORY_MESSAGES = env.int("SMART_COACH_MAX_HISTORY_MESSAGES", default=16)
SMART_COACH_RAG_CONTEXT_MAX_CHARS = env.int("SMART_COACH_RAG_CONTEXT_MAX_CHARS", default=10000)

UNSPLASH_ACCESS_KEY = env("UNSPLASH_ACCESS_KEY", default="")
