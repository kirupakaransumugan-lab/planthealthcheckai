from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.database import init_db
from app.routers.person import router as person_router
from app.routers.plant import router as plant_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the MySQL tables on startup if they do not exist yet
    init_db()
    yield


app = FastAPI(
    title="AI Plant Health Analysis API",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(person_router)
app.include_router(plant_router)


@app.get("/")
def root():
    return {
        "message": "AI Plant Health API is running"
    }