#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import asyncio
from fastapi.templating import Jinja2Templates

class FrontEndService:
    def __init__(self):
        # Опасно: если переменной нет, будет ошибка. Добавь проверку.
        base_url = os.getenv("EDGE_ROUTER_SERVICE_URL", "http://edge-router:8080")
        prefix = os.getenv("API_PREFIX", "/api/v1")
        self.edge_router_url = f"{base_url.rstrip('/')}{prefix}"
        
        # Переносим создание шаблонов в класс как статику или инициализируем один раз
        self.templates = Jinja2Templates(directory='app/templates')
        self.templates.env.globals["site_name"] = "Логистика Асфальта"

    async def get_index_page(self, request):
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Сразу подставляем /api/v1 если его нет в self.edge_router_url
            tasks = [
                client.get(f'{self.edge_router_url}/plants'),
                client.get(f'{self.edge_router_url}/trucks'),
                client.get(f'{self.edge_router_url}/orders'),
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            plants = self._parse_res(responses[0], "plants")
            trucks = self._parse_res(responses[1], "trucks")
            orders = self._parse_res(responses[2], "orders")

        context = {
            "request": request,
            "title": "Мониторинг",
            "plants": plants,
            "trucks": trucks,
            "orders": orders,
        }

        return self.templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context=context
        )

    def _parse_res(self, res, key):
        # Если res это исключение (из gather), вернем пустой список
        if isinstance(res, httpx.Response) and res.status_code == 200:
            try:
                data = res.json()
                return data.get(key, [])
            except:
                return []
        return []

