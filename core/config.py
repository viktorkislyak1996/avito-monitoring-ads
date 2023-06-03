import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MONGO_URL: str | None = os.getenv("MONGO_URL")
    DB_NAME: str | None = os.getenv("MONGO_DB")
    DB_USER: str | None = os.getenv("MONGO_USER")
    DB_PASSWORD: str | None = os.getenv("MONGO_PASSWORD")


settings = Settings()

# @lru_cache()
# def get_settings():
#     return Settings()
