#!/usr/bin/env python3
# -- coding: utf-8 --

import os
import math
import httpx
from datetime import datetime, timezone

class CalculatorService:
    def __init__(self):
        self.logistics_service_url = os.getenv("LOGISTICS_SERVICE_URL", "http://logistics:8082").rstrip('/')
        self.ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml:8085").rstrip('/') + "/predict"
        self.osrm_url = os.getenv("OSRM_SERVICE_URL", "http://router.project-osrm.org").rstrip('/')

        self.T_START = 165.0
        self.T_MIN = 120.0 
        self.K_COOLING = 0.04 

    async def calculate_optimal_delivery(self, section_id: int, volume: float):
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                sec_res = await client.get(f"{self.logistics_service_url}/sections")
                sections = sec_res.json().get('sections', [])
                target_section = next((s for s in sections if s['id'] == section_id), None)
                
                plant_res = await client.get(f"{self.logistics_service_url}/plants")
                plants = plant_res.json().get('plants', [])
            except Exception as e:
                return {"is_possible": False, "reason": f"Ошибка связи с базой: {str(e)}"}

            if not target_section:
                return {"is_possible": False, "reason": f"Участок {section_id} не найден"}
            if not plants:
                return {"is_possible": False, "reason": "В базе нет ни одного завода (АБЗ)"}

            target_coords = self._parse_wkt(target_section['start_location'])
            
            # Погода
            weather_data = {}
            try:
                w_res = await client.post(self.ml_service_url, json={
                    "lat": target_coords[1], "lon": target_coords[0],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                weather_data = w_res.json()
                current_t_env = weather_data.get('temperature', 15.0)
            except:
                current_t_env = 15.0

            best_plant = None
            max_arrival_temp = -1.0
            debug_info = []
            closest_dist = float('inf')
            closest_plant_name = ""

            for plant in plants:
                plant_coords = self._parse_wkt(plant['location'])
                
                # Реальное расстояние через OSRM
                osrm_req = f"{self.osrm_url}/route/v1/driving/{plant_coords[0]},{plant_coords[1]};{target_coords[0]},{target_coords[1]}?overview=false"
                
                try:
                    r = await client.get(osrm_req)
                    data = r.json()
                    if data.get('code') == 'Ok':
                        route = data['routes'][0]
                        dist_km = route['distance'] / 1000.0
                        duration_h = route['duration'] / 3600.0
                        
                        t_arrival = current_t_env + (self.T_START - current_t_env) * math.exp(-self.K_COOLING * duration_h)

                        if dist_km < closest_dist:
                            closest_dist = dist_km
                            closest_plant_name = plant['name']

                        debug_info.append({
                            "plant": plant['name'],
                            "route_km": round(dist_km, 2),
                            "expected_t": round(t_arrival, 1),
                            "time_min": int(duration_h * 60)
                        })

                        if t_arrival >= self.T_MIN and t_arrival > max_arrival_temp:
                            max_arrival_temp = t_arrival
                            best_plant = {
                                "id": plant['id'],
                                "name": plant['name'],
                                "temp": round(t_arrival, 1),
                                "dist": round(dist_km, 2),
                                "time": int(duration_h * 60)
                            }
                except:
                    continue

            if best_plant:
                return {
                    "is_possible": True,
                    "optimal_plant_id": best_plant['id'],
                    "optimal_plant_name": best_plant['name'],
                    "arrival_temp": best_plant['temp'],
                    "travel_time_min": best_plant['time'],
                    "distance_km": best_plant['dist'],
                    "green_window": next((h['timestamp'] for h in weather_data.get('hourly_forecast', []) if h['recommendation'] == "МОЖНО РАБОТАТЬ"), None)
                }
            else:
                return {
                    "is_possible": False,
                    "reason": "Ни один АБЗ не подходит по температуре",
                    "closest_plant": {"name": closest_plant_name, "distance_km": round(closest_dist, 2)},
                    "debug_log": debug_info,
                    "hint": f"Проверьте координаты. Сейчас участок: {target_coords}. Долгота должна быть ~30, Широта ~60."
                }

    def _parse_wkt(self, wkt_str: str) -> list:
        try:
            content = wkt_str.replace("POINT", "").replace("(", "").replace(")", "").strip()
            parts = content.split()
            v1, v2 = float(parts[0]), float(parts[1])
            # Если число > 45, это Широта (для СЗ РФ). Если нет - Долгота.
            if v1 > v2: lat, lon = v1, v2
            else: lon, lat = v1, v2
            return [lon, lat]
        except:
            return [30.3, 59.8]
