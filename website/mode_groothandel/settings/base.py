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
    "constance",
    "constance.backends.database",
    "users",
    "mutations",
    "invoices",
    "sendcloud",
    "snelstart",
    "uphance",
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
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_SCHEMA_CLASS": "tosti.api.openapi.CustomAutoSchema",
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

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "SNELSTART_GROOTBOEKCODE_BTW_HOOG": (
        "",
        "Grootboekcode to book BTW hoog items under in Snelstart",
        str,
    ),
    "SNELSTART_GROOTBOEKCODE_BTW_GEEN": ("", "Grootboekcode to book BTW geen items under in Snelstart", str),
    "SNELSTART_GROOTBOEKCODE_SHIPPING_COSTS_BTW_HOOG": (
        "",
        "Grootboekcode to book BTW hoog shipping costs under in Snelstart",
        str,
    ),
    "SNELSTART_GROOTBOEKCODE_SHIPPING_COSTS_BTW_GEEN": (
        "",
        "Grootboekcode to book BTW geen shipping costs under in Snelstart",
        str,
    ),
    "SNELSTART_BTW_HOOG_NAME": {
        "Hoog",
        "Constant for amount of BTW Hoog post.",
        str,
    },
    "SNELSTART_BTW_GEEN_NAME": {
        "Geen",
        "Constant for amount of BTW Geen post.",
        str,
    }
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Snelstart settings": (
        "SNELSTART_GROOTBOEKCODE_BTW_HOOG",
        "SNELSTART_GROOTBOEKCODE_BTW_GEEN",
        "SNELSTART_GROOTBOEKCODE_SHIPPING_COSTS_BTW_HOOG",
        "SNELSTART_GROOTBOEKCODE_SHIPPING_COSTS_BTW_GEEN",
        "SNELSTART_BTW_HOOG_NAME",
        "SNELSTART_BTW_GEEN_NAME"
    ),
}

# Sites app
SITE_ID = 1

DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 14
