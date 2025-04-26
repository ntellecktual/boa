from django.apps import AppConfig


class BoaappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "boaapp"
    def ready(self):
        import boaapp.templatetags.camel_filters
