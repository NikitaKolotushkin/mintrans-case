#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class MaintenanceTaskBase(BaseModel):
    truck_id: Optional[int] = None
    reason: str
    is_completed: bool = False

class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass

class MaintenanceTaskResponse(MaintenanceTaskCreate):
    id: int
    created_at: datetime

class MaintenanceTaskListResponse(BaseModel):
    maintenance_tasks: List[MaintenanceTaskResponse]
