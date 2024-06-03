import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "mutations",
    "sendcloud",
    "snelstart",
    "uphance",
    "invoices",
    "credit_notes",
    "mode_groothandel",
]

AUTH_USER_MODEL = "users.User"

ANONYMOUS_USER_NAME = None

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mode_groothandel.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "mode_groothandel.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Amsterdam"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/(?:api|user/oauth)/.*"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

# OAUTH
OAUTH2_PROVIDER = {
    "ALLOWED_REDIRECT_URI_SCHEMES": ["https"],
    "SCOPES": {
        "read": "Authenticated read access to the website",
        "write": "Authenticated write access to the website",
    },
}
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"

# Sites app
SITE_ID = 1

DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 14

UPHANCE_USERNAME = os.environ.get("UPHANCE_USERNAME", None)
UPHANCE_PASSWORD = os.environ.get("UPHANCE_PASSWORD", None)
UPHANCE_ORGANISATION = os.environ.get("UPHANCE_ORGANISATION", None)
UPHANCE_CACHE_PATH = os.environ.get("UPHANCE_CACHE_PATH", ".uphance-cache")

UPHANCE_SECRET = os.environ.get("UPHANCE_SECRET", None)

SNELSTART_CLIENT_KEY = os.environ.get("SNELSTART_CLIENT_KEY", None)
SNELSTART_SUBSCRIPTION_KEY = os.environ.get("SNELSTART_SUBSCRIPTION_KEY", None)
SNELSTART_CACHE_PATH = os.environ.get("SNELSTART_CACHE_PATH", ".snelstart-cache")

SENDCLOUD_PUBLIC_KEY = os.environ.get("SENDCLOUD_PUBLIC_KEY", None)
SENDCLOUD_PRIVATE_KEY = os.environ.get("SENDCLOUD_PRIVATE_KEY", None)
