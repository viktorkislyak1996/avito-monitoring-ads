from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status
from starlette.responses import JSONResponse

from app.api.actions.counters import db_add_counters, db_get_counters
from app.api.actions.queries import db_add_queries, db_get_queries, db_get_query
from app.db.database import get_db
from app.db.models import CounterOut, Query
from app.scrapers.avito_avs_scraper import AvitoAvsScraper

# create the instance for the routes
ads_router = APIRouter()


@ads_router.get("/queries", response_model=list[Query])
async def list_queries(db: AsyncIOMotorClient = Depends(get_db)):
    queries = await db_get_queries(db)
    return queries


@ads_router.get("/counters", response_model=list[CounterOut])
async def list_counters(db: AsyncIOMotorClient = Depends(get_db)):
    query: dict = dict()
    counters = await db_get_counters(query, db)
    return counters


@ads_router.post("/add", response_model=Query)
async def add_query(query: Query = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    query_to_scrape = await db_add_queries(query, db)

    # scrape avito
    scraper = AvitoAvsScraper(query_to_scrape)
    counter = scraper.get_ads_number()
    if not counter:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during scrape Avito. Please try again later.",
        )

    await db_add_counters(counter, db)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=query_to_scrape)


@ads_router.get("/stat/{query_id}/{time_interval}", response_model=list[CounterOut])
async def stat_counters(
    query_id: str, time_interval: int, db: AsyncIOMotorClient = Depends(get_db)
):
    start_date = datetime.now() - timedelta(hours=time_interval)
    query = {"$and": [{"query_id": query_id}, {"timestamp": {"$gte": start_date}}]}
    counters = await db_get_counters(query, db)
    return counters


@ads_router.get("/top/{query_id}", response_model=list[dict])
async def top_ads(query_id: str, db: AsyncIOMotorClient = Depends(get_db)):
    query = await db_get_query(query_id, db)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found.",
        )

    scraper = AvitoAvsScraper(query)
    result = scraper.get_top_ads()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during scrape avito. Please try again later.",
        )
    return result
