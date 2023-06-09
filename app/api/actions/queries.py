from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.models import Query


async def db_get_queries(db: AsyncIOMotorClient) -> list[Query]:
    queries = []
    cursor = db.query_collection.find({})
    async for document in cursor:
        queries.append(Query(**document))
    return queries


async def db_get_query(query_id: str, db: AsyncIOMotorClient) -> dict:
    query = await db.query_collection.find_one({"_id": query_id})
    return query


async def db_add_queries(query: Query | dict, db: AsyncIOMotorClient) -> dict:
    if isinstance(query, Query):
        query = jsonable_encoder(query)

    # check if the record exists in database
    query_to_scrape = await db.query_collection.find_one(
        {"search_phrase": query["search_phrase"]}
    )

    if not query_to_scrape:
        new_query = await db.query_collection.insert_one(query)
        query_to_scrape = await db.query_collection.find_one(
            {"_id": new_query.inserted_id}
        )

    return query_to_scrape
