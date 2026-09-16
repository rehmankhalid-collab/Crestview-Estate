from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment variables / a .env file.

    See .env.example for what each value does and how to fill it in.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./crestview.db"

    # SMTP / lead notification email. TODO: replace with real credentials
    # before launch — see .env.example. When smtp_host is empty, email
    # sending is skipped (leads are still persisted to the database).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from_email: str = "noreply@crestviewestates.com"
    lead_notification_email: str = "hello@crestviewestates.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()
