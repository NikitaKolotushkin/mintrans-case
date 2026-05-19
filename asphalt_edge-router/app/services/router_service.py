#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx

from asphalt_common import *

from fastapi import HTTPException
from typing import Optional


class RouterService:

    def __init__(self):
        self.front_end_service_url = os.getenv("FRONT_END_SERVICE_URL")
        self.logistics_service_url = os.getenv("LOGISTICS_SERVICE_URL")
        self.weather_service_url = os.getenv("WEATHER_SERVICE_URL")
        self.calculator_service_url = os.getenv("CALCULATOR_SERVICE_URL")
        self.ml_service_url = os.getenv("ML_SERVICE_URL")

    # PLANTS

    async def get_plants_from_logistics_service(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{self.logistics_service_url}/plants')
            response.raise_for_status()
            return response.json()

    async def post_plant_to_logistics_service(self, plant_data: PlantCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/plants', 
                json=plant_data.model_dump()
            )
            response.raise_for_status()
            return response.json()

    # SECTIONS

    async def get_sections_from_logistics_service(self, is_active: bool):
        async with httpx.AsyncClient() as client:
            params = {"is_active": is_active}
            response = await client.get(f'{self.logistics_service_url}/sections', params=params)
            response.raise_for_status()
            return response.json()

    async def post_section_to_logistics_service(self, section_data: SectionCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/sections', 
                json=section_data.model_dump()
            )
            response.raise_for_status()
            return response.json()

    # TRUCKS

    async def get_trucks_from_logistics_service(self, status: Optional[TruckStatus] = None):
        async with httpx.AsyncClient() as client:
            params = {"status": status.value} if status else {}
            response = await client.get(f'{self.logistics_service_url}/trucks', params=params)
            response.raise_for_status()
            return response.json()

    async def post_truck_to_logistics_service(self, truck_data: TruckCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/trucks', 
                json=truck_data.model_dump()
            )
            response.raise_for_status()
            return response.json()

    # ORDERS

    async def get_orders_from_logistics_service(self, status: Optional[OrderStatus] = None):
        async with httpx.AsyncClient() as client:
            params = {"status": status.value} if status else {}
            response = await client.get(f'{self.logistics_service_url}/orders', params=params)
            response.raise_for_status()
            return response.json()

    async def post_order_to_logistics_service(self, order_data: OrderCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/orders', 
                json=order_data.model_dump()
            )
            response.raise_for_status()
            return response.json()

    # TRIPS

    async def get_trips_from_logistics_service(self, order_id: Optional[int] = None):
        async with httpx.AsyncClient() as client:
            params = {"order_id": order_id} if order_id else {}
            response = await client.get(f'{self.logistics_service_url}/trips', params=params)
            response.raise_for_status()
            return response.json()

    async def post_trip_to_logistics_service(self, trip_data: TripCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/trips', 
                json=trip_data.model_dump()
            )
            response.raise_for_status()
            return response.json()

    # MAINTENANCE

    async def get_maintenance_tasks_from_logistics_service(self, is_completed: Optional[bool] = None):
        async with httpx.AsyncClient() as client:
            params = {"is_completed": is_completed} if is_completed is not None else {}
            response = await client.get(f'{self.logistics_service_url}/maintenance', params=params)
            response.raise_for_status()
            return response.json()

    async def post_maintenance_task_to_logistics_service(self, task_data: MaintenanceTaskCreate):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.logistics_service_url}/maintenance', 
                json=task_data.model_dump()
            )
            response.raise_for_status()
            return response.json()


    # ML METHODS

    async def predict_asphalt_work(self, predict_data: PredictRequest):
        """Отправка данных на расчет в ML сервис"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ml_service_url}/predict",
                json=predict_data.model_dump(mode='json') 
            )
            response.raise_for_status()
            return response.json()

    async def get_ml_service_health(self):
        """Проверка статуса ML сервиса"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.ml_service_url}/health")
            response.raise_for_status()
            return response.json()

    # CALCULATOR

    async def calculate_order_in_calculator_service(self, data: CalculateOrderRequest):
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{self.calculator_service_url}/calculate', json=data.model_dump())
            response.raise_for_status()
            return response.json()
