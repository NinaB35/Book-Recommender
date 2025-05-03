import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Основной класс настроек приложения.
    """

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_URL: URL | None = None

    TEST_DB_NAME: str
    TEST_DB_URL: URL | None = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file="env/app.env")

    def __init__(self):
        super().__init__()
        self.DB_URL = URL.create(
            drivername="postgresql+asyncpg",
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
            database=self.DB_NAME
        )
        self.TEST_DB_URL = URL.create(
            drivername="postgresql+asyncpg",
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
            database=self.TEST_DB_NAME
        )


settings = Settings()
logger.info("Environment variables loaded")
