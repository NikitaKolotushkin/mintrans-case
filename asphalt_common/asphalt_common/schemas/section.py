#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class SectionBase(BaseModel):
    name: str
    km_start: int
    km_end: int
    center_location: str = Field(description="Геометрия Point (WKT или GeoJSON)")
    is_active: bool = True

class SectionCreate(SectionBase):
    pass

class SectionResponse(SectionCreate):
    id: int
    created_at: datetime

class SectionListResponse(BaseModel):
    sections: List[SectionResponse]
