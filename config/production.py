#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .base import BaseConfig

import os


class ProductionConfig(BaseConfig):
    """Конфигурация для продакшена"""
    DEVELOPMENT: bool = False
    DEBUG: bool = False
    RELOAD: bool = False
