from django.conf import settings


def pytest_configure(config):
    """Override database to SQLite in-memory for all test runs."""
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    # Disable cachalot in tests to avoid cache interference
    if 'cachalot' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [a for a in settings.INSTALLED_APPS if a != 'cachalot']
    # Disable debug_toolbar in tests — its staticfiles panel wraps storage and
    # still hits ManifestStaticFilesStorage even after we override STORAGES.
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = [a for a in settings.INSTALLED_APPS if a != 'debug_toolbar']
        settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if 'debug_toolbar' not in m]
    # Use simple static files storage so tests don't need collectstatic / manifest
    settings.STORAGES = {
        **getattr(settings, 'STORAGES', {}),
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
