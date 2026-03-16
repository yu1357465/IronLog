from django.apps import AppConfig

class CoreConfig(AppConfig):
    # Decision: Define the application configuration.
    # Intent: This ensures the Django project registry correctly discovers and loads the 'core' module and its associated sub-components (like migrations and custom template tags).
    name = 'core'