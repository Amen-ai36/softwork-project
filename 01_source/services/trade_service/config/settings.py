from services.common.settings import build_settings

globals().update(
    build_settings(
        service_name="trade-service",
        app_config="services.trade_service.trade.apps.TradeConfig",
        root_urlconf="services.trade_service.config.urls",
        wsgi_application="services.trade_service.config.wsgi.application",
        db_env="TRADE_DB_NAME",
    )
)
