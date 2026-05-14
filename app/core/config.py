from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fornecimentos-service"
    app_env: str = "local"
    database_url: str
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_fornecimentos: str = "portal-b2b.fornecimentos"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
