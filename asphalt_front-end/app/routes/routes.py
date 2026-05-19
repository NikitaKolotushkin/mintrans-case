#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httpx
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from app.services.front_end_service import FrontEndService


router = APIRouter(tags=['frontend'])

_service_instance = FrontEndService()

async def get_front_end_service():
    return _service_instance

@router.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_api(path: str, request: Request, service: FrontEndService = Depends(get_front_end_service)):
    # ВАЖНО: service.edge_router_url уже содержит /api/v1 (из __init__)
    # request.url.path тоже содержит /api/v1. 
    # Нужно получить только базовый хост, чтобы не было /api/v1/api/v1/trucks
    base_url = service.edge_router_url.replace("/api/v1", "").rstrip("/")
    target_url = f"{base_url}{request.url.path}"
    
    print(f"DEBUG PROXY: Forwarding to -> {target_url}")

    async with httpx.AsyncClient() as client:
        try:
            proxy_resp = await client.request(
                method=request.method,
                url=target_url,
                params=dict(request.query_params),
                content=await request.body(),
                # Строго приводим заголовки к строкам
                headers={str(k): str(v) for k, v in request.headers.items() 
                         if k.lower() not in ("host", "content-length")},
                timeout=10.0
            )
            
            # Исключаем проблемные заголовки
            EXCLUDED_HEADERS = {"content-encoding", "content-length", "transfer-encoding", "connection"}
            headers = {str(k): str(v) for k, v in proxy_resp.headers.items() 
                       if k.lower() not in EXCLUDED_HEADERS}

            return Response(
                content=proxy_resp.content,
                status_code=proxy_resp.status_code,
                headers=headers
            )
        except Exception as e:
            print(f"DEBUG PROXY ERROR: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")

@router.get('/', response_class=HTMLResponse)
async def home(request: Request, service: FrontEndService = Depends(get_front_end_service)):
    # Убираем try-except здесь, чтобы увидеть реальный Traceback в логах контейнера, если упадет
    return await service.get_index_page(request)
