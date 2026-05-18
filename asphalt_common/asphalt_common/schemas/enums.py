#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum

class TruckStatus(str, Enum):
    IDLE = 'IDLE'
    LOADING = 'LOADING'
    IN_TRANSIT = 'IN_TRANSIT'
    UNLOADING = 'UNLOADING'
    RETURNING = 'RETURNING'
    MAINTENANCE = 'MAINTENANCE'

class OrderStatus(str, Enum):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    REDIRECTED = 'REDIRECTED'

class OrderType(str, Enum):
    ASPHALT = 'ASPHALT'
    TECHNICAL_FLUIDS = 'TECHNICAL_FLUIDS'
