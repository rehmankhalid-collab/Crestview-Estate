import os
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Serverless hosts (Vercel sets VERCEL=1) only allow writes under /tmp;
# everything else in the deployed filesystem is read-only. Falling back to
# "./crestview.db" there raises "unable to open database file" on every
# request. This only picks the *path*; set DATABASE_URL explicitly (ideally
# to a real hosted Postgres — see README) for anything beyond a demo, since
# /tmp is wiped between cold starts and isn't shared across instances.
_DEFAULT_DB_URL = (
    "sqlite:////tmp/crestview.db" if os.environ.get("VERCEL") else "sqlite:///./crestview.db"
)


class Settings(BaseSettings):
    """App configuration, loaded from environment variables / a .env file.

    See .env.example for what each value does and how to fill it in.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = _DEFAULT_DB_URL

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

    @model_validator(mode="before")
    @classmethod
    def _blank_env_vars_mean_unset(cls, data):
        # A platform's dashboard (e.g. Vercel) lets you add an env var with
        # an empty value, which isn't the same as not setting it — pydantic
        # can't parse "" as a bool/int (smtp_port, smtp_use_tls) and would
        # otherwise crash the whole app at import time over one blank
        # field. Drop blank entries so they fall through to the field's
        # real default instead.
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v != ""}
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
