import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.handlers import ads_router
from app.db.database import close_database_connection, connect_to_database

app = FastAPI(title="avito-ads-monitoring")

# middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# set routes to the app instance
app.include_router(ads_router, prefix="/api", tags=["ads"])


@app.on_event("startup")
async def startup():
    await connect_to_database()


@app.on_event("shutdown")
async def shutdown():
    await close_database_connection()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
