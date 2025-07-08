from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db.session import init_db
from api.events import router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Init method for DB before starting app")
    init_db()
    yield
    # clean up


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(events_router, prefix="/api/events")


@app.get("/healthz/")
def health_check_endpoint():
    return {"status": "ok"}
