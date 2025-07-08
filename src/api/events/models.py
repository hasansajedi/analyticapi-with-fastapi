from datetime import datetime
from typing import Optional, ClassVar
from sqlmodel import Field, SQLModel
from timescaledb import TimescaleModel


class EventCreateSchema(SQLModel):
    page: str
    user_agent: Optional[str] = Field(default="", index=True)
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)


class EventModel(TimescaleModel, table=True):
    page: str = Field(index=True)
    user_agent: Optional[str] = Field(default="", index=True)
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)

    __chunk_time_interval__: ClassVar[str] = "INTERVAL 1 day"
    __drop_after__: ClassVar[str] = "INTERVAL 3 months"


class EventListSchema(SQLModel):
    results: list[EventModel]
    count: int


class EventBucketSchema(SQLModel):
    bucket: datetime
    page: str
    operating_system: Optional[str] = ""
    avg_duration: Optional[float] = 0.0
    count: int
