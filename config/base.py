#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings
from typing import Optional

import os


class BaseConfig(BaseSettings):
    """Базовые настройки для всех окружений"""
    # APP_NAME: str = "Asphalt"

    API_PREFIX: str = "/api"

    DOCS_URL: Optional[str] = None
    REDOC_URL: Optional[str] = None
    OPENAPI_URL: Optional[str] = None
    
    model_config = {
        'case_sensitive': True,
        'env_file': 'app.env'
    }
