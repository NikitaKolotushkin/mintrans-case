#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict

class PredictRequest(BaseModel):
    timestamp: datetime
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)

class HourlyForecast(BaseModel):
    timestamp: datetime
    probability: float
    recommendation: str

class PredictResponse(BaseModel):
    request_time: datetime
    coordinates: Dict[str, float]
    hourly_forecast: List[HourlyForecast]
    overall_probability_4h: float
    overall_recommendation: str
    note: str