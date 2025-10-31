from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from app.config.credentials_config import config


async def connect_to_mongodb(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(config.DATABASE_URL)
    app.mongodb = app.mongodb_client.get_database(config.DB_NAME)
    print("MongoDB connected")


async def disconnect_from_mongodb(app: FastAPI):
    app.mongodb_client.close()
    print("MongoDB disconnected")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await connect_to_mongodb(app)
        yield
    finally:
        await disconnect_from_mongodb(app)
