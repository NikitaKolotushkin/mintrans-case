#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException, status
from httpx import HTTPStatusError
from asphalt_common import *

from app.services.calculator_service import CalculatorService

router = APIRouter()
calculator_service = CalculatorService()

@router.post("/calculate", status_code=status.HTTP_200_OK, tags=["Calculator"])
async def calculate_optimal_order(request: CalculateOrderRequest):
    """
    Рассчитать оптимальный завод для доставки смеси на указанный участок.
    Учитывает расстояние, остывание (Закон Ньютона) и погодные условия.
    """
    try:
        result = await calculator_service.calculate_optimal_delivery(
            section_id=request.section_id,
            volume=request.volume
        )
        return result
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка внешнего сервиса: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
