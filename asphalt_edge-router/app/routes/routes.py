#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from httpx import HTTPStatusError
from fastapi import APIRouter, Query, HTTPException, Response, Request, status
from asphalt_common import *

from app.services.router_service import RouterService


router = APIRouter()
router_service = RouterService()


# PLANTS

@router.get("/plants", response_model=PlantListResponse, tags=["Plants"])
async def get_plants(request: Request):
    """Получить список всех заводов"""
    try:
        plants_data = await router_service.get_plants_from_logistics_service()
        return plants_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plants", response_model=PlantResponse, status_code=status.HTTP_201_CREATED, tags=["Plants"])
async def create_plant(request: Request, plant: PlantCreate):
    """Добавить новый завод"""
    try:
        plant_data = await router_service.post_plant_to_logistics_service(plant)
        return plant_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SECTIONS

@router.get("/sections", response_model=SectionListResponse, tags=["Sections"])
async def get_sections(request: Request, is_active: bool = Query(True, description="Показывать только активные участки")):
    """Получить список участков (с фильтрацией по активности)"""
    try:
        sections_data = await router_service.get_sections_from_logistics_service(is_active=is_active)
        return sections_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED, tags=["Sections"])
async def create_section(request: Request, section: SectionCreate):
    """Добавить новый ремонтируемый участок"""
    try:
        section_data = await router_service.post_section_to_logistics_service(section)
        return section_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TRUCKS

@router.get("/trucks", response_model=TruckListResponse, tags=["Trucks"])
async def get_trucks(request: Request, truck_status: TruckStatus = Query(None, alias="status", description="Фильтр по статусу машины")):
    """Получить список грузовиков (можно отфильтровать по статусу, например: IDLE, IN_TRANSIT)"""
    try:
        trucks_data = await router_service.get_trucks_from_logistics_service(status=truck_status)
        return trucks_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/trucks", response_model=TruckResponse, status_code=status.HTTP_201_CREATED, tags=["Trucks"])
async def create_truck(request: Request, truck: TruckCreate):
    """Зарегистрировать новый грузовик"""
    try:
        truck_data = await router_service.post_truck_to_logistics_service(truck)
        return truck_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ORDERS

@router.get("/orders", response_model=OrderListResponse, tags=["Orders"])
async def get_orders(request: Request, order_status: OrderStatus = Query(None)):
    """Получить список заказов"""
    try:
        orders_data = await router_service.get_orders_from_logistics_service(status=order_status)
        return orders_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(request: Request, order: OrderCreate):
    """Создать заказ на поставку асфальта или тех. жидкостей"""
    try:
        order_data = await router_service.post_order_to_logistics_service(order)
        return order_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TRIPS

@router.get("/trips", response_model=TripListResponse, tags=["Trips"])
async def get_trips(request: Request, order_id: int = Query(None, description="Получить все рейсы для конкретного заказа")):
    """Получить историю рейсов"""
    try:
        trips_data = await router_service.get_trips_from_logistics_service(order_id=order_id)
        return trips_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED, tags=["Trips"])
async def create_trip(request: Request, trip: TripCreate):
    """Создать рейс (назначить машину на заказ)"""
    try:
        trip_data = await router_service.post_trip_to_logistics_service(trip)
        return trip_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MAINTENANCE (Обслуживание)

@router.get("/maintenance", response_model=MaintenanceTaskListResponse, tags=["Maintenance"])
async def get_maintenance_tasks(request: Request, is_completed: bool = Query(None)):
    """Список задач на ремонт/обслуживание"""
    try:
        tasks_data = await router_service.get_maintenance_tasks_from_logistics_service(is_completed=is_completed)
        return tasks_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/maintenance", response_model=MaintenanceTaskResponse, status_code=status.HTTP_201_CREATED, tags=["Maintenance"])
async def create_maintenance_task(request: Request, task: MaintenanceTaskCreate):
    """Отправить машину на обслуживание"""
    try:
        task_data = await router_service.post_maintenance_task_to_logistics_service(task)
        return task_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ML PREDICTIONS

@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK,  tags=["ML"], summary="Запрос прогноза возможности укладки асфальта")
async def predict_asphalt(request: Request, data: PredictRequest):
    """
    Прокси-запрос к ML микросервису для получения прогноза.
    Принимает координаты (lat, lon) и время (timestamp).
    """
    try:
        prediction = await router_service.predict_asphalt_work(data)
        return prediction
    except HTTPStatusError as e:
        detail = e.response.json().get("detail", str(e))
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Edge Router Error (ML): {str(e)}"
        )


# CALCULATOR

@router.post("/calculate", response_model=CalculateOrderResponse, tags=["Calculator"])
async def calculate_order(request: Request, data: CalculateOrderRequest):
    try:
        # Идем в калькулятор
        res = await router_service.calculate_order_in_calculator_service(data)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
