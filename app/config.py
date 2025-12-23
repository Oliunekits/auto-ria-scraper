from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    start_url: str = Field(default="https://auto.ria.com/uk/car/used/", alias="START_URL")
    scrape_at: str = Field(default="12:00", alias="SCRAPE_AT")  # HH:MM
    dump_at: str = Field(default="12:10", alias="DUMP_AT")      # HH:MM
    timezone: str = Field(default="Europe/Kyiv", alias="TIMEZONE")

    max_pages: int = Field(default=50, alias="MAX_PAGES")
    concurrency: int = Field(default=20, alias="CONCURRENCY")
    request_timeout: int = Field(default=25, alias="REQUEST_TIMEOUT")
    request_delay_min: float = Field(default=0.0, alias="REQUEST_DELAY_MIN")
    request_delay_max: float = Field(default=0.2, alias="REQUEST_DELAY_MAX")


    db_name: str = Field(default="autoria", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    db_host: str = Field(default="db", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
