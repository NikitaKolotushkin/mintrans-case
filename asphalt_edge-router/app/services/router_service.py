#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx

from asphalt_common import TruckResponse, TruckStatus, OrderCreate

from fastapi import HTTPException
from typing import Optional


class RouterService:


    def __init__(self):
        self.front_end_service_url = os.getenv("FRONT_END_SERVICE_URL")
        self.logistics_service_url = os.getenv("USERS_SERVICE_URL")
        self.weather_service_url = os.getenv("EVENTS_SERVICE_URL")
        self.calculator_service_url = os.getenv("MAILER_SERVICE_URL")
        self.ml_service_url = os.getenv("MAPS_SERVICE_URL")

    async def get_all_events_from_event_service(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{self.events_service_url}/events/')
            
            return response.json()
