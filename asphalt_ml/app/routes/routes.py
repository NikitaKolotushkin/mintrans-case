#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from httpx import HTTPStatusError
from fastapi import APIRouter, HTTPException, Request, status
from asphalt_common import PredictRequest, PredictResponse

router = APIRouter()


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK, tags=["ML Predictions"], summary="Выполнить расчет прогноза")
async def predict_asphalt_work(request: Request, data: PredictRequest):
    """
    Принимает координаты и время, возвращает вероятность успешности работ.
    Использует агрегацию данных Open-Meteo и Яндекс.Погоды.
    """
    ml_service = request.app.state.ml_service
    
    try:
        result = await ml_service.get_asphalt_prediction(data)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Data validation error: {str(e)}"
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"External Weather Service Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal ML Engine Error: {str(e)}"
        )

# SYSTEM

@router.get("/health", tags=["System"])
async def health_check(request: Request):
    """Проверка доступности модели и API ключей"""
    ml_service = request.app.state.ml_service
    return {
        "status": "online",
        "model_loaded": ml_service.model is not None,
        "yandex_key_configured": bool(ml_service.yandex_api_key)
    }
