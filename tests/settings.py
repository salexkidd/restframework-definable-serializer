INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'definable_serializer',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "secret_key_for_testing"
MIDDLEWARE_CLASSES = []
ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django_settings_contextprocessor.context_processors.settings_module_name',
                'django_settings_contextprocessor.context_processors.django_debug_flg',
                'django_settings_contextprocessor.context_processors.djagno_settings_data',
                'django_projectname.context_processors.project_name',
                'apps.systemsettings.context_processors.other_system_token',
                'apps.systemsettings.context_processors.sales_tax_data',
            ],
        },
    },
]
