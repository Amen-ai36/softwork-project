from services.common.settings import build_settings

globals().update(
    build_settings(
        service_name="user-service",
        app_config="services.user_service.users.apps.UsersConfig",
        root_urlconf="services.user_service.config.urls",
        wsgi_application="services.user_service.config.wsgi.application",
        db_env="USER_DB_NAME",
    )
)
