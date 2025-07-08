from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import func, case
from timescaledb.hyperfunctions import time_bucket

from api.db.session import get_session
from .models import (
    EventModel,
    EventListSchema,
    EventCreateSchema,
    EventBucketSchema,
)

router = APIRouter()

DEFAULT_LOOKUP_PAGES = [
    "/",
    "/about",
    "/blog",
    "/products",
    "/login",
    "/signup",
    "/dashboard",
    "/settings",
    "/contact",
    "/pricing",
]


@router.get("/", response_model=List[EventBucketSchema])
def read_events(
    duration: str = Query(default="1 day"),
    pages: List = Query(default=None),
    session: Session = Depends(get_session),
) -> EventListSchema:
    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = (
        pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES
    )
    os_case = case(
        (EventModel.user_agent.ilike("%windows%"), "Windows"),
        (EventModel.user_agent.ilike("%macintosh%"), "MacOS"),
        (EventModel.user_agent.ilike("%iphone%"), "iOS"),
        (EventModel.user_agent.ilike("%android%"), "Android"),
        (EventModel.user_agent.ilike("%linux%"), "Linux"),
        else_="Other",
    ).label("operating_system")
    query = (
        select(
            bucket.label("bucket"),
            os_case,
            EventModel.page.label("page"),
            func.avg(EventModel.duration).label("avg_duration"),
            func.count().label("count"),
        )
        .where(
            EventModel.page.in_(lookup_pages),
        )
        .group_by(bucket, os_case, EventModel.page)
        .order_by(bucket, os_case, EventModel.page)
    )
    results = session.exec(query).fetchall()
    # query = select(EventModel).order_by(EventModel.updated_at.desc()).limit(10)
    # results = session.exec(query).all()
    return results


@router.post("/", response_model=EventModel)
def create_events(
    payload: EventCreateSchema, session: Session = Depends(get_session)
) -> EventModel:
    data = payload.model_dump()
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/{event_id}", response_model=EventModel)
def get_event(event_id: int, session: Session = Depends(get_session)) -> EventModel:
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Event not found.")
    return result
