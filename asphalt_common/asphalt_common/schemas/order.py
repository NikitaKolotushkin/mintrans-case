#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .enums import OrderType, OrderStatus

class OrderBase(BaseModel):
    type: OrderType = OrderType.ASPHALT
    plant_id: Optional[int] = None
    section_id: Optional[int] = None
    ordered_tons: float
    delivered_tons: float = 0.0
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
