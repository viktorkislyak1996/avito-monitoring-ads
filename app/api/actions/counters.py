from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient

from app.db.models import Counter, CounterOut


async def db_get_counters(query: dict, db: AsyncIOMotorClient) -> list[CounterOut]:
    counters = []
    cursor = db.counter_collection.find(query)
    async for document in cursor:
        counter = Counter(**document)
        counters.append(CounterOut.from_orm(counter))
    return counters


async def db_add_counters(counter: Counter | dict, db: AsyncIOMotorClient) -> dict:
    if isinstance(counter, Counter):
        counter = jsonable_encoder(counter)

    new_counter = await db.counter_collection.insert_one(counter)
    inserted_counter = await db.query_collection.find_one(
        {"_id": new_counter.inserted_id}
    )
    return inserted_counter
