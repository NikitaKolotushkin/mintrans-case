#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class SectionBase(BaseModel):
    name: str
    start_location: str = Field(description="WKT Point начала участка (например, POINT(37.6 55.7))")
    end_location: str = Field(description="WKT Point конца участка")
    is_active: bool = True

class SectionCreate(SectionBase):
    pass

class SectionResponse(SectionBase):
    id: int
    created_at: datetime

class SectionListResponse(BaseModel):
    sections: List[SectionResponse]
