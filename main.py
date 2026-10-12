from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.models import init_db
from apps.views.auth import router as auth_router
from apps.views.main import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(product_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
