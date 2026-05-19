#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse, HTMLResponse

from app.services.front_end_service import FrontEndService


router = APIRouter(tags=['frontend'])


async def get_front_end_service():
    return FrontEndService()


# @router.get('/favicon.ico', include_in_schema=False)
# async def favicon(request: Request, service: FrontEndService = Depends(get_front_end_service)):
#     return FileResponse('app/static/src/img/favicon.svg')


@router.get('/', response_class=HTMLResponse)
async def home(
    request: Request,
    service: FrontEndService = Depends(get_front_end_service)
):
    """
    Главная страница MVP (Дашборд).
    Собирает данные о заводах, машинах и заказах на одной странице.
    """
    try:
        return await service.get_index_page(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    