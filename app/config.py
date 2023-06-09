import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    db_path: str | None = os.getenv("MONGO_URL")
    db_name: str | None = os.getenv("MONGO_DB")
    db_user: str | None = os.getenv("MONGO_USER")
    db_password: str | None = os.getenv("MONGO_PASSWORD")
    max_db_conn_count: str | None = os.getenv("MAX_CONNECTIONS_COUNT")
    min_db_conn_count: str | None = os.getenv("MIN_CONNECTIONS_COUNT")


@lru_cache()
def get_settings():
    return Settings()
