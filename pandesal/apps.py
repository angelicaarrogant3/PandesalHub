from django.apps import AppConfig


class PandesalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pandesal'
    
    def ready(self):
        """Import signals when app is ready"""
        import pandesal.signals
