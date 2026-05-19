#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import joblib
import logging
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        # Путь теперь точно соответствует твоей структуре
        self.model_path = os.getenv("MODEL_PATH", "app/models/asphalt_model_calibrated.pkl")
        self.yandex_api_key = os.getenv("YANDEX_WEATHER_API_KEY", "")
        self.model = None
        
        # ЭТОТ СПИСОК ДОЛЖЕН БЫТЬ ИДЕНТИЧЕН СПИСКУ ИЗ ОРИГИНАЛЬНОГО КОДА
        self.features_list = [
            "temp", "precip_mm", "precip_prob", "wind_speed", "wind_gust",
            "humidity", "cloud_cover", "pressure_mm", "visibility_m",
            "hour", "day_of_week", "is_daytime", "temp_lag_1", "temp_lag_2",
            "wind_lag_1", "precip_prob_lag_1", "temp_rolling_mean_3h", "wind_rolling_max_3h"
        ]
        
        self.om_mapping = {
            "temperature_2m": "temp",
            "precipitation": "precip_mm",
            "precipitation_probability": "precip_prob",
            "wind_speed_10m": "wind_speed",
            "wind_gusts_10m": "wind_gust",
            "relative_humidity_2m": "humidity",
            "cloud_cover": "cloud_cover",
            "surface_pressure": "pressure_mm",
            "visibility": "visibility_m",
        }

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"✅ Модель успешно загружена: {self.model_path}")
            else:
                logger.error(f"❌ Файл модели не найден: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели: {e}")

    async def get_asphalt_prediction(self, req) -> dict:
        if not self.model:
            raise ValueError("Модель не загружена на сервере")

        # 1. Получаем данные (6 часов истории + 6 часов прогноза)
        df_weather = await self._fetch_combined_weather(req.lat, req.lon, req.timestamp)
        
        # 2. Генерируем фичи (лаги и скользящие средние)
        df_features = self._prepare_features(df_weather)
        
        # 3. Берем только нужные 4 часа, начиная с запрошенного времени
        start_utc = req.timestamp.replace(tzinfo=timezone.utc) if req.timestamp.tzinfo is None else req.timestamp
        df_forecast = df_features[df_features["timestamp"] >= start_utc].head(4)
        
        if df_forecast.empty:
            logger.warning("Не найдено данных на указанное время, берем последние доступные")
            df_forecast = df_features.tail(4)

        # 4. Проверка колонок (Модель упадет, если порядок или состав признаков не тот)
        for col in self.features_list:
            if col not in df_forecast.columns:
                df_forecast[col] = 0.0 # Фолбэк для отсутствующих лагов

        # 5. Предсказание
        X = df_forecast[self.features_list]
        probs = self.model.predict_proba(X)[:, 1]

        hourly_forecast = []
        for i, (idx, row) in enumerate(df_forecast.iterrows()):
            p = float(probs[i])
            hourly_forecast.append({
                "timestamp": row["timestamp"],
                "probability": round(p, 3),
                "recommendation": self._get_label(p)
            })

        overall_p = float(np.min(probs)) if len(probs) > 0 else 0.0

        return {
            "request_time": req.timestamp,
            "coordinates": {"lat": req.lat, "lon": req.lon},
            "hourly_forecast": hourly_forecast,
            "overall_probability_4h": round(overall_p, 3),
            "overall_recommendation": self._get_label(overall_p),
            "note": f"Агрегация: Open-Meteo + Yandex. Использовано {len(df_weather)} точек метеоданных."
        }

    def _get_label(self, p: float) -> str:
        if p >= 0.75: return "МОЖНО РАБОТАТЬ"
        if p >= 0.45: return "С ОСТОРОЖНОСТЬЮ"
        return "НЕЛЬЗЯ"

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy().sort_values("timestamp")
        
        # Базовые временные признаки
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["is_daytime"] = df["hour"].between(6, 20).astype(int)

        # Лаги (важно для модели)
        for lag in [1, 2]:
            for col, prefix in [("temp", "temp"), ("wind_speed", "wind"), ("precip_prob", "precip_prob")]:
                if col in df.columns:
                    df[f"{prefix}_lag_{lag}"] = df[col].shift(lag).bfill()

        # Скользящие окна
        df["temp_rolling_mean_3h"] = df["temp"].rolling(3, min_periods=1).mean()
        df["wind_rolling_max_3h"] = df["wind_speed"].rolling(3, min_periods=1).max()
        
        return df.fillna(0)

    async def _fetch_combined_weather(self, lat, lon, start_time):
        dt_utc = start_time.replace(tzinfo=timezone.utc) if start_time.tzinfo is None else start_time
        
        # Собираем данные параллельно
        hist_task = self._get_om(lat, lon, dt_utc - timedelta(hours=10), dt_utc, is_archive=True)
        fore_task = self._get_om(lat, lon, dt_utc, dt_utc + timedelta(hours=10), is_archive=False)
        yand_task = self._get_yandex(lat, lon)
        
        h_df, f_df, y_df = await asyncio.gather(hist_task, fore_task, yand_task)
        
        # Склеиваем OM
        full_df = pd.concat([h_df, f_df], ignore_index=True).drop_duplicates("timestamp")
        
        # Накладываем Яндекс сверху (он точнее)
        if not y_df.empty:
            full_df = pd.concat([full_df, y_df]).drop_duplicates("timestamp", keep="last")
            
        return full_df.sort_values("timestamp").reset_index(drop=True)

    async def _get_om(self, lat, lon, start, end, is_archive=False):
        base = "https://archive-api.open-meteo.com/v1/archive" if is_archive else "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "hourly": ",".join(self.om_mapping.keys()),
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "timezone": "UTC"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(base, params=params)
                if r.status_code != 200: return pd.DataFrame()
                data = r.json().get("hourly", {})
                df = pd.DataFrame(data)
                if df.empty: return df
                df["timestamp"] = pd.to_datetime(df["time"], utc=True)
                df = df.rename(columns=self.om_mapping)
                if "pressure_mm" in df.columns: df["pressure_mm"] *= 0.750062
                return df
            except Exception as e:
                logger.error(f"OpenMeteo Error: {e}")
                return pd.DataFrame()

    async def _get_yandex(self, lat, lon):
        if not self.yandex_api_key: return pd.DataFrame()
        headers = {"X-Yandex-Weather-Key": self.yandex_api_key}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get("https://api.weather.yandex.ru/v2/forecast", 
                                   params={"lat": lat, "lon": lon, "hours": "true"}, 
                                   headers=headers)
                if r.status_code != 200: return pd.DataFrame()
                
                rows = []
                for fc in r.json().get("forecasts", []):
                    for h in fc.get("hours", []):
                        rows.append({
                            "timestamp": datetime.fromtimestamp(h["hour_ts"], tz=timezone.utc),
                            "temp": h.get("temp"),
                            "precip_mm": h.get("prec_mm", 0),
                            "precip_prob": h.get("prec_percent", 0),
                            "wind_speed": h.get("wind_speed"),
                            "wind_gust": h.get("wind_gust"),
                            "humidity": h.get("humidity"),
                            "cloud_cover": h.get("cloudness", 0) * 100,
                            "pressure_mm": h.get("pressure_mm"),
                            "visibility_m": h.get("visibility", 10) * 1000
                        })
                return pd.DataFrame(rows)
            except Exception as e:
                logger.error(f"Yandex Error: {e}")
                return pd.DataFrame()
