from datetime import datetime, timedelta

import uvicorn
from fastapi import Body, FastAPI
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from core.database import counter_collection, query_collection
from core.models import Counter, CounterOut, Query
from scrapers.avito_avs_scraper import AvitoAvsScraper

app = FastAPI()


@app.get(
    "/queries",
    response_description="List of all the queries",
    response_model=list[Query],
)
async def list_queries():
    queries = []
    cursor = query_collection.find({})
    async for document in cursor:
        queries.append(Query(**document))
    return queries


@app.get(
    "/counters",
    response_description="List of all the counters",
    response_model=list[CounterOut],
)
async def list_counters():
    counters = []
    cursor = counter_collection.find({})
    async for document in cursor:
        counter = Counter(**document)
        counters.append(CounterOut.from_orm(counter))
    return counters


@app.post("/add", response_description="Add a search query", response_model=Query)
async def add_query(query: Query = Body(...)):
    query = jsonable_encoder(query)
    new_query = await query_collection.insert_one(query)
    created_query = await query_collection.find_one({"_id": new_query.inserted_id})

    scraper = AvitoAvsScraper(created_query)
    content = scraper.get_content()
    scraper.get_ads_number(content)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=new_query.inserted_id
    )


@app.get(
    "/stat/{query_id}/{time_interval}",
    response_description="List of counters by query id for the time interval",
    response_model=list[CounterOut],
)
async def stat_counters(query_id: str, time_interval: int):
    counters = []
    start_date = datetime.now() - timedelta(hours=time_interval)
    query = {"$and": [{"query_id": query_id}, {"timestamp": {"$gte": start_date}}]}
    cursor = counter_collection.find(query)
    async for document in cursor:
        counter = Counter(**document)
        counters.append(CounterOut.from_orm(counter))
    return counters


if __name__ == "__main__":
    uvicorn.run("core.main:app", host="0.0.0.0", port=8000, reload=True)
