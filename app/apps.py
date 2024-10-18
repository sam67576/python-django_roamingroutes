from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'app'
    verbose_name = 'My Custom App'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Import and register any signal handlers or other setup code
        pass
