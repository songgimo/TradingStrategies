from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = "StockTrader"

    # 1. DB Settings
    db_host: str
    db_user: str

    # 2. Important key settings
    open_dart_key: SecretStr
    upbit_key: SecretStr
    upbit_secret: SecretStr

    db_password: SecretStr

    # 3. Celery Settings
    celery_broker_url: str
    celery_result_backend_url: str

    environment: str = "development"

    json_file_path: str = "../statics"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
