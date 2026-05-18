#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class TripBase(BaseModel):
    order_id: Optional[int] = None
    truck_id: Optional[int] = None
    dispatched_at: Optional[datetime] = None
    initial_temp_c: Optional[float] = None
    redirected_to_section_id: Optional[int] = None
    completed_at: Optional[datetime] = None

class TripCreate(TripBase):
    pass

class TripResponse(TripCreate):
    id: int

class TripListResponse(BaseModel):
    trips: List[TripResponse]