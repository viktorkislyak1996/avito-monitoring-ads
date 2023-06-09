from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field

from app.db.database import PyObjectId


class Query(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    search_phrase: str = Field(...)
    region: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}
        schema_extra = {
            "example": {"search_phrase": "iPhone 14 Pro Max", "region": "Москва"}
        }


class Counter(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    query_id: PyObjectId = Field(default_factory=PyObjectId)
    quantity: int = Field(...)
    timestamp: datetime = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda oid: str(oid),
            datetime: lambda dt: dt.isoformat(),
        }
        schema_extra = {
            "example": {
                "query_id": "6478e527e80a148f8f230544",
                "quantity": 1650,
                "timestamp": datetime(2023, 10, 10),
            }
        }

    @property
    def counter_timestamp(self):
        return self.timestamp.strftime("%B %d, %Y; %H:%M")


class CounterOut(BaseModel):
    quantity: int = Field(...)
    counter_timestamp: str = Field(..., computed=True)

    class Config:
        orm_mode = True
        exclude = {"timestamp", "id", "query_id"}
