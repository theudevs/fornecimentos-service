from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "fornecimentos-service"
    port: int = 5003
    app_env: str = "local"
    database_url: str
    db_schema: str = "portal_b2b"
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = ""
    kafka_fail_on_publish_error: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def app_name(self) -> str:
        return self.service_name


@lru_cache
def get_settings() -> Settings:
    return Settings()
