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
    "FOOTER_CREDITS_TEXT": (
        "TOSTI - Tartarus Order System for Take-away Items",
        "Text to display in the footer credits",
        str,
    ),
    "CLEANING_SCHEME_URL": ("", "URL to the cleaning scheme to be accepted when submitting a borrel form", str),
    "SILVASOFT_API_URL": ("https://rest-api.silvasoft.nl/rest/", "Endpoint for Silvasoft API", str),
    "SILVASOFT_USERNAME": ("", "Username for Silvasoft integration", str),
    "SILVASOFT_API_KEY": ("", "API key for Silvasoft integration", str),
    "MAXIMUM_SYNC_PER_RUN": (15, "Maximum amount of synchronizations to run per hour", int),
    "BORREL_SEND_BORREL_RESERVATION_REQUEST_EMAILS_TO": (
        "noreply@example.com",
        "Where to send borrel reservation request notifications to (e-mail address)",
        str,
    ),
    "VENUES_SEND_RESERVATION_REQUEST_EMAILS_TO": (
        "noreply@example.com, noreply@example.com",
        "Where to send venue reservation request notifications to (e-mail address), enter multiple addresses by using a comma (,)",
        str,
    ),
    "SHIFTS_DEFAULT_MAX_ORDERS_TOTAL": (70, "Default maximum number of orders per shift", int),
    "THALIEDJE_STOP_PLAYERS_AT": ("21:00", "Time to stop the players. Should be aligned on 5 minutes", str),
    "THALIEDJE_START_PLAYERS_AT": (
        "08:00",
        "Time to start the players (only on weekdays). Should be aligned on 5 minutes",
        str,
    ),
    "THALIEDJE_HOLIDAY_ACTIVE": (
        False,
        "If enabled, the player will not start playing automatically at the start of the day",
        bool,
    ),
    "THALIEDJE_START_PLAYER_URI": ("", "URI to start playing when the player starts automatically.", str),
    "THALIEDJE_MAX_SONG_REQUESTS_PER_HOUR": (
        10,
        "Maximum number of song requests per hour before a user is blacklisted",
        int,
    ),
    "STATISTICS_BORREL_CATEGORY": (
        0,
        "The object ID of the Category of Borrel products to show on the statistics screen.",
        int,
    ),
    "FRIDGE_REQUIRE_DAILY_OPENING": (
        False,
        "If enabled, every day the fridge needs to be openend at least once by a person with open_always permissions, "
        "to be able to open it again.",
        bool,
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "General settings": (
        "FOOTER_CREDITS_TEXT",
        "CLEANING_SCHEME_URL",
        "STATISTICS_BORREL_CATEGORY",
    ),
    "Silvasoft settings": (
        "SILVASOFT_API_URL",
        "SILVASOFT_USERNAME",
        "SILVASOFT_API_KEY",
        "MAXIMUM_SYNC_PER_RUN",
    ),
    "E-mail settings": (
        "BORREL_SEND_BORREL_RESERVATION_REQUEST_EMAILS_TO",
        "VENUES_SEND_RESERVATION_REQUEST_EMAILS_TO",
    ),
    "Shifts settings": ("SHIFTS_DEFAULT_MAX_ORDERS_TOTAL",),
    "Thaliedje settings": (
        "THALIEDJE_STOP_PLAYERS_AT",
        "THALIEDJE_START_PLAYERS_AT",
        "THALIEDJE_HOLIDAY_ACTIVE",
        "THALIEDJE_START_PLAYER_URI",
        "THALIEDJE_MAX_SONG_REQUESTS_PER_HOUR",
    ),
    "Fridge settings": ("FRIDGE_REQUIRE_DAILY_OPENING",),
}

# Sites app
SITE_ID = 1

DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 14
