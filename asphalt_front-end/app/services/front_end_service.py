#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import asyncio

from fastapi import Request
from fastapi.templating import Jinja2Templates

class FrontEndService:
    
    def __init__(self):
        self.edge_router_url = os.getenv("EDGE_ROUTER_SERVICE_URL")
        self.templates = Jinja2Templates(directory='app/templates')
        
        # Вместо сложного request_context можно добавить простые глобальные переменные
        self.templates.env.globals["site_name"] = "Логистика Асфальта"

    async def get_index_page(self, request: Request):
        """
        Главная страница Dashboard: собирает всё в один контекст
        """
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                tasks = [
                    client.get(f'{self.edge_router_url}/plants'),
                    client.get(f'{self.edge_router_url}/trucks'),
                    client.get(f'{self.edge_router_url}/orders'),
                    client.get(f'{self.edge_router_url}/maintenance')
                ]
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                plants = self._parse_res(responses[0], "plants")
                trucks = self._parse_res(responses[1], "trucks")
                orders = self._parse_res(responses[2], "orders")
                tasks_list = self._parse_res(responses[3], "maintenance_tasks")

            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                plants, trucks, orders, tasks_list = [], [], [], []

        # Формируем стандартный контекст
        context = {
            "request": request,
            "title": "Мониторинг",
            # "plants": plants,
            # "trucks": trucks,
            # "orders": orders,
            # "maintenance": tasks_list
        }

        return self.templates.TemplateResponse("index.html", context)

    def _parse_res(self, response, key):
        """Вспомогательный метод: если запрос успешен — берем ключ, иначе — []"""
        if isinstance(response, httpx.Response) and response.status_code == 200:
            return response.json().get(key, [])
        return []
