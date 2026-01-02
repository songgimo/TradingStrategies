from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_FOLDER_PATH = BASE_DIR / "statics"
SQLITE_DB_FOLDER_PATH = BASE_DIR / "database"


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

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
