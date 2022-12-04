"""
Django settings for siteVoyance project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""


import os
from pathlib import Path
import django_heroku


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY") or "testkey"
# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = "PROD" not in os.environ

ALLOWED_HOSTS = ["herokuapps.com", "localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ball8.apps.Ball8Config",
    "clairvoyance.apps.ClairvoyanceConfig",
    "accounts.apps.AccountsConfig",
    "import_export",
    "responses.apps.ResponsesConfig",
]

##################################################
CRONJOBS = [("30 8 * * *", "accounts.cron.send_emails")]
##################################################

######################AUTH#########################
AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTIFICATION_BACKENDS = "accounts.backends.CustomUserAuth"
LOGOUT_REDIRECT_URL = "home"
LOGIN_REDIRECT_URL = "history"
LOGIN_URL = "login"
###################################################


########################EMAIL######################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
EMAIL_PORT = 587
# EMAIL_PORT_SSL = 465
EMAIL_HOST_USER = (
    "patricia.nunes.tarot@gmail.com"  # os.environ.get("EMAIL_HOST_USER")
)
EMAIL_HOST_PASSWORD = "Ruben1Mara2"  # os.environ.get("EMAIL_HOST_PASSWORD")

###################################################

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "siteVoyanceconfig.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "siteVoyanceconfig.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = (
    {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "lastProject",
            "USER": "Nuno",
            "PASSWORD": "bcxau9p^^123.",
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }
    if "PROD" in os.environ
    else {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-US"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

########################HEROKU###############################
django_heroku.settings(locals())
#############################################################
