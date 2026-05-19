#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.config import get_config
from app.routes.routes import router
from app.services.ml_service import MLService

config = get_config()

ml_service = MLService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом: выполняется при старте и остановке
    """
    ml_service.load_model()
    
    yield

app = FastAPI(
    title="Asphalt ML Predictor",
    lifespan=lifespan,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL,
)

app.state.ml_service = ml_service

app.include_router(router)
