#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .enums import TruckStatus

class TruckBase(BaseModel):
    plate_number: str
    capacity_tons: float = 20.0
    status: TruckStatus = TruckStatus.IDLE
    home_plant_id: Optional[int] = None

class TruckCreate(TruckBase):
    pass

class TruckResponse(TruckCreate):
    id: int
    created_at: datetime

class TruckListResponse(BaseModel):
    trucks: List[TruckResponse]
