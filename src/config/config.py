from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import logging
import sys
from pathlib import Path

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_FOLDER_PATH = BASE_DIR / "statics"
SQLITE_DB_FOLDER_PATH = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"


class Settings(BaseSettings):
    app_name: str = "StockTrader"

    # 1. DB Settings
    db_host: str
    db_user: str
    db_password: SecretStr

    # 2. Important key settings
    open_dart_key: SecretStr
    upbit_key: SecretStr
    upbit_secret: SecretStr

    google_api_key: SecretStr

    # 3. Celery Settings
    celery_broker_url: str
    celery_result_backend_url: str

    # 4. LangSmith Settings
    lang_smith_api_key: str

    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )


def setup_logging():
    """
    Args:
        env: 'development', 'staging', 'production'
    """

    env = settings.environment
    LOG_DIR.mkdir(exist_ok=True)

    log_levels = {
        'development': logging.DEBUG,
        'staging': logging.INFO,
        'production': logging.WARNING
    }

    root_logger = logging.getLogger()
    root_logger.setLevel(log_levels.get(env, logging.INFO))

    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if env == 'development' else logging.INFO)

    console_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(
        filename=LOG_DIR / 'app.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    file_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)

    error_handler = RotatingFileHandler(
        filename=LOG_DIR / 'error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    root_logger.addHandler(error_handler)

    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('celery').setLevel(logging.INFO)

    logging.getLogger('backend.domain').setLevel(logging.DEBUG)
    logging.getLogger('backend.infrastructure').setLevel(logging.INFO)

    if env == 'production':
        import json

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': self.formatTime(record),
                    'level': record.levelname,
                    'logger': record.name,
                    'function': record.funcName,
                    'line': record.lineno,
                    'message': record.getMessage(),
                }

                if record.exc_info:
                    log_data['exception'] = self.formatException(record.exc_info)

                if hasattr(record, 'task_id'):
                    log_data['task_id'] = record.task_id
                if hasattr(record, 'ticker'):
                    log_data['ticker'] = record.ticker

                return json.dumps(log_data, ensure_ascii=False)

        json_handler = RotatingFileHandler(
            filename=LOG_DIR / 'app.json.log',
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setFormatter(JsonFormatter())
        root_logger.addHandler(json_handler)

    logging.info(f"Logging configured for {env} environment")

settings = Settings()
setup_logging()
