import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


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


client = AsyncIOMotorClient(
    settings.MONGO_URL,
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
)
db = client[settings.DB_NAME]
query_collection = db.get_collection("query_collection")
counter_collection = db.get_collection("counter_collection")
# db.collection.createIndex( { user: 1, title: 1, Bank: 1 }, {unique:true} )

# async def create_mongo_client() -> AsyncIOMotorClient:
#     try:
#         client = AsyncIOMotorClient(
#             settings.MONGO_URL,
#             username=settings.MONGO_USER,
#             password=settings.MONGO_PASSWORD,
#         )
#         logging.info('Connected to mongo.')
#     except Exception as e:
#         logging.exception(f'Could not connect to mongo: {e}')
#         raise
#     return client
#
#
# async def get_database(client: AsyncIOMotorClient):
#     db = client[settings.MONGO_DB]
#     return db


# import os
# from dotenv import load_dotenv
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# import logging
#
# from .config import Config
#
# MONGO_URLS = "mongodb://localhost:27017/avito_ads"
#
# client = AsyncIOMotorClient(MONGO_URLS)
#
# load_dotenv()
#
# db_client: AsyncIOMotorClient = None
#
#
# async def get_db() -> AsyncIOMotorClient:
#     db_name = Config.app_settings.get('db_name')
#     return db_client[db_name]
#
#
# async def connect_and_init_db():
#     global db_client
#     try:
#         db_client = AsyncIOMotorClient(
#             Config.app_settings.get('mongodb_url'),
#             username=Config.app_settings.get('db_username'),
#             password=Config.app_settings.get('db_password'),
#             uuidRepresentation="standard"
#         )
#         logging.info('Connected to mongo.')
#     except Exception as e:
#         logging.exception(f'Could not connect to mongo: {e}')
#         raise
#
#
# async def close_db_connect():
#     global db_client
#     if db_client is None:
#         logging.warning('Connection is None, nothing to close.')
#         return
#     db_client.close()
#     db_client = None
#     logging.info('Mongo connection closed.')
#
