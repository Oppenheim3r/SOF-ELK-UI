"""
Django settings for sof_elk_ui project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sof-elk-ui-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # For development only, restrict in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sof_elk_ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sof_elk_ui.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SOF-ELK specific settings
SOF_ELK_PATHS = {
    'LOG_DIRS': {
        'aws': '/logstash/aws/',
        'azure': '/logstash/azure/',
        'gcp': '/logstash/gcp/',
        'gws': '/logstash/gws/',
        'httpd': '/logstash/httpd/',
        'kape': '/logstash/kape/',
        'kubernetes': '/logstash/kubernetes/',
        'microsoft365': '/logstash/microsoft365/',
        'nfarch': '/logstash/nfarch/',
        'passivedns': '/logstash/passivedns/',
        'plaso': '/logstash/plaso/',
        'syslog': '/logstash/syslog/',
        'zeek': '/logstash/zeek/',
    },
    'COMMANDS': {
        'clear_elasticsearch': '/usr/local/sbin/sof-elk_clear.py',
        'update_sof_elk': '/usr/local/sbin/sof-elk_update.sh',
        'nfdump_to_sof_elk': 'nfdump2sof-elk.sh',
        'aws_vpcflow_to_sof_elk': 'aws-vpcflow2sof-elk.sh',
        'azure_vpcflow_to_sof_elk': 'azure-vpcflow2sof-elk.py',
    },
    'CONFIG_DIR': '/etc/logstash/conf.d/',
    'SOF_ELK_REPO': '/usr/local/sof-elk/',
}

# Maximum file upload size (10MB)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
