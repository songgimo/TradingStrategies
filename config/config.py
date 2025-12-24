from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = "StockTrader"

    # 1. Base settings
    db_host: str
    db_user: str

    # 2. Important key settings
    open_dart_key: SecretStr
    upbit_key: SecretStr
    upbit_secret: SecretStr

    db_password: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
