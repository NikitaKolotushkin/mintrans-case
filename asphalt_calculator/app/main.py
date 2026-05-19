#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import time

from fastapi import FastAPI, Request
from starlette.responses import Response
from typing import Dict, Any, Optional

from app.config import get_config
from app.routes.routes import router


config = get_config()

app = FastAPI(
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL,
)

app.include_router(router)
