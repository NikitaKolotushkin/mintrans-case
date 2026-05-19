#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.services.logistics_service import LogisticsService
from asphalt_common import *

router = APIRouter()

async def get_logistics_service(session: AsyncSession = Depends(get_async_session)):
    return LogisticsService(session)

# PLANTS
@router.get("/plants", response_model=PlantListResponse, tags=["Plants"])
async def get_all_plants(service: LogisticsService = Depends(get_logistics_service)):
    return await service.get_all_plants()

@router.post("/plants", response_model=PlantResponse, status_code=201, tags=["Plants"])
async def create_plant(plant: PlantCreate, service: LogisticsService = Depends(get_logistics_service)):
    try:
        return await service.create_plant(plant)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# TRUCKS
@router.get("/trucks", response_model=TruckListResponse, tags=["Trucks"])
async def get_all_trucks(status: TruckStatus = None, service: LogisticsService = Depends(get_logistics_service)):
    return await service.get_all_trucks(status)

@router.post("/trucks", response_model=TruckResponse, status_code=201, tags=["Trucks"])
async def create_truck(truck: TruckCreate, service: LogisticsService = Depends(get_logistics_service)):
    return await service.create_truck(truck)

# SECTIONS
@router.get("/sections", response_model=SectionListResponse, tags=["Sections"])
async def get_all_sections(
    is_active: bool = Query(True), 
    service: LogisticsService = Depends(get_logistics_service)
):
    """Получить список участков (используется edge-router-ом)"""
    return await service.get_all_sections(is_active=is_active)

@router.post("/sections", response_model=SectionResponse, status_code=201, tags=["Sections"])
async def create_section(section: SectionCreate, service: LogisticsService = Depends(get_logistics_service)):
    return await service.create_section(section)

# ORDERS
@router.get("/orders", response_model=OrderListResponse, tags=["Orders"])
async def get_all_orders(status: OrderStatus = None, service: LogisticsService = Depends(get_logistics_service)):
    return await service.get_all_orders(status)

@router.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
async def create_order(order: OrderCreate, service: LogisticsService = Depends(get_logistics_service)):
    return await service.create_order(order)

# TRIPS
@router.get("/trips", response_model=TripListResponse, tags=["Trips"])
async def get_all_trips(
    order_id = Query(None), 
    service: LogisticsService = Depends(get_logistics_service)
):
    return await service.get_all_trips(order_id=order_id)

@router.post("/trips", response_model=TripResponse, status_code=201, tags=["Trips"])
async def create_trip(trip: TripCreate, service: LogisticsService = Depends(get_logistics_service)):
    return await service.create_trip(trip)
