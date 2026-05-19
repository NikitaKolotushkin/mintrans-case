#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

DB_HOST = os.getenv("LOGISTICS_DB_HOST", "postgres-logistics")
DB_PORT = os.getenv("LOGISTICS_DB_PORT", "5432")
DB_NAME = os.getenv("LOGISTICS_DB_NAME", "asphalt_logistics")

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME} as user {DB_USER}")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session