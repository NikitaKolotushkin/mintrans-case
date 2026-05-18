#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from httpx import HTTPStatusError
from fastapi import APIRouter, Query, HTTPException, Response, Request, status
from asphalt_common import *

from app.services.router_service import RouterService


router = APIRouter()
router_service = RouterService()


async def proxy_request(method: str, url: str, json_data: dict = None, params: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=json_data, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Logistics service unavailable")


# PLANTS


@router.get("/plants", response_model=PlantListResponse, tags=["Plants"])
async def get_plants():
    """Получить список всех заводов"""
    return await proxy_request("GET", f"{LOGISTICS_URL}/plants")

@router.post("/plants", response_model=PlantResponse, status_code=status.HTTP_201_CREATED, tags=["Plants"])
async def create_plant(plant: PlantCreate):
    """Добавить новый завод"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/plants", json_data=plant.model_dump())


# SECTIONS


@router.get("/sections", response_model=SectionListResponse, tags=["Sections"])
async def get_sections(is_active: bool = Query(True, description="Показывать только активные участки")):
    """Получить список участков (с фильтрацией по активности)"""
    return await proxy_request("GET", f"{LOGISTICS_URL}/sections", params={"is_active": is_active})

@router.post("/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED, tags=["Sections"])
async def create_section(section: SectionCreate):
    """Добавить новый ремонтируемый участок"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/sections", json_data=section.model_dump())


# TRUCKS


@router.get("/trucks", response_model=TruckListResponse, tags=["Trucks"])
async def get_trucks(status: TruckStatus = Query(None, description="Фильтр по статусу машины")):
    """Получить список грузовиков (можно отфильтровать по статусу, например: IDLE, IN_TRANSIT)"""
    params = {"status": status.value} if status else {}
    return await proxy_request("GET", f"{LOGISTICS_URL}/trucks", params=params)

@router.post("/trucks", response_model=TruckResponse, status_code=status.HTTP_201_CREATED, tags=["Trucks"])
async def create_truck(truck: TruckCreate):
    """Зарегистрировать новый грузовик"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/trucks", json_data=truck.model_dump())


# ORDERS


@router.get("/orders", response_model=OrderListResponse, tags=["Orders"])
async def get_orders(order_status: OrderStatus = Query(None)):
    """Получить список заказов"""
    params = {"status": order_status.value} if order_status else {}
    return await proxy_request("GET", f"{LOGISTICS_URL}/orders", params=params)

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(order: OrderCreate):
    """Создать заказ на поставку асфальта или тех. жидкостей"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/orders", json_data=order.model_dump())


# TRIPS


@router.get("/trips", response_model=TripListResponse, tags=["Trips"])
async def get_trips(order_id: int = Query(None, description="Получить все рейсы для конкретного заказа")):
    """Получить историю рейсов"""
    params = {"order_id": order_id} if order_id else {}
    return await proxy_request("GET", f"{LOGISTICS_URL}/trips", params=params)

@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED, tags=["Trips"])
async def create_trip(trip: TripCreate):
    """Создать рейс (назначить машину на заказ)"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/trips", json_data=trip.model_dump())



# MAINTENANCE (Обслуживание)


@router.get("/maintenance", response_model=MaintenanceTaskListResponse, tags=["Maintenance"])
async def get_maintenance_tasks(is_completed: bool = Query(None)):
    """Список задач на ремонт/обслуживание"""
    params = {"is_completed": is_completed} if is_completed is not None else {}
    return await proxy_request("GET", f"{LOGISTICS_URL}/maintenance", params=params)

@router.post("/maintenance", response_model=MaintenanceTaskResponse, status_code=status.HTTP_201_CREATED, tags=["Maintenance"])
async def create_maintenance_task(task: MaintenanceTaskCreate):
    """Отправить машину на обслуживание"""
    return await proxy_request("POST", f"{LOGISTICS_URL}/maintenance", json_data=task.model_dump())
