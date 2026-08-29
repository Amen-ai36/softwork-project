from services.common.settings import build_settings

globals().update(
    build_settings(
        service_name="lifestyle-service",
        app_config="services.lifestyle_service.lifestyle.apps.LifestyleConfig",
        root_urlconf="services.lifestyle_service.config.urls",
        wsgi_application="services.lifestyle_service.config.wsgi.application",
        db_env="LIFESTYLE_DB_NAME",
    )
)
