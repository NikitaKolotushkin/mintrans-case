#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class PlantBase(BaseModel):
    name: str
    capacity_per_hour: float
    bunker_capacity: float
    location: str = Field(description="Геометрия Point (WKT или GeoJSON)")

class PlantCreate(PlantBase):
    pass

class PlantResponse(PlantCreate):
    id: int
    created_at: datetime

class PlantListResponse(BaseModel):
    plants: List[PlantResponse]
