import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings

db_client: AsyncIOMotorClient = None
settings = get_settings()


async def get_db() -> AsyncIOMotorClient:
    db_name = settings.db_name
    return db_client[db_name]


async def connect_to_database():
    global db_client
    try:
        db_client = AsyncIOMotorClient(
            settings.db_path,
            username=settings.db_user,
            password=settings.db_password,
            maxPoolSize=settings.max_db_conn_count,
            minPoolSize=settings.min_db_conn_count,
        )
        logging.info("Connected to mongo.")
    except Exception as e:
        logging.exception(f"Could not connect to mongo: {e}")
        raise


async def close_database_connection():
    global db_client
    if not db_client:
        logging.warning("Connection not found, nothing to close.")
        return
    db_client.close()
    db_client = None
    logging.info("Mongo connection closed.")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
