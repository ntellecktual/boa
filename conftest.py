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
