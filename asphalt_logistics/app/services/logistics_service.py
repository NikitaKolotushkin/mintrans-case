#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_AsText, ST_GeomFromText

from app.models.logistics import PlantModel, SectionModel, TruckModel, OrderModel, TripModel
import asphalt_common.schemas as schemas

class LogisticsService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # PLANTS 

    async def create_plant(self, plant_data: schemas.plant.PlantCreate) -> schemas.plant.PlantResponse:
        """Создать новый завод"""
        new_plant = PlantModel(
            name=plant_data.name,
            capacity_per_hour=plant_data.capacity_per_hour,
            bunker_capacity=plant_data.bunker_capacity,
            location=ST_GeomFromText(plant_data.location, 4326)
        )
        self.session.add(new_plant)
        await self.session.commit()
        await self.session.refresh(new_plant)
        
        return await self.get_plant_by_id(new_plant.id)

    async def get_all_plants(self) -> schemas.plant.PlantListResponse:
        """Получить все заводы"""
        result = await self.session.execute(
            select(
                PlantModel.id, PlantModel.name, PlantModel.capacity_per_hour,
                PlantModel.bunker_capacity, ST_AsText(PlantModel.location).label('location'),
                PlantModel.created_at
            )
        )
        plants = result.mappings().all()
        
        return schemas.plant.PlantListResponse(
            plants=[schemas.plant.PlantResponse(**p) for p in plants]
        )

    async def get_plant_by_id(self, plant_id: int) -> schemas.plant.PlantResponse:
        """Получить завод по ID"""
        result = await self.session.execute(
            select(
                PlantModel.id, PlantModel.name, PlantModel.capacity_per_hour,
                PlantModel.bunker_capacity, ST_AsText(PlantModel.location).label('location'),
                PlantModel.created_at
            ).where(PlantModel.id == plant_id)
        )
        plant = result.mappings().one_or_none()
        
        if not plant:
            raise ValueError(f"Plant with id {plant_id} not found")
            
        return schemas.plant.PlantResponse(**plant)

    # SECTIONS 

    async def create_section(self, section_data: schemas.section.SectionCreate) -> schemas.section.SectionResponse:
        """Добавить новый ремонтируемый участок"""
        new_section = SectionModel(
            name=section_data.name,
            km_start=section_data.km_start,
            km_end=section_data.km_end,
            center_location=ST_GeomFromText(section_data.center_location, 4326),
            is_active=section_data.is_active
        )
        self.session.add(new_section)
        await self.session.commit()
        await self.session.refresh(new_section)
        
        return await self.get_section_by_id(new_section.id)

    async def get_all_sections(self, is_active: bool = True) -> schemas.section.SectionListResponse:
        """Получить список участков с фильтрацией"""
        result = await self.session.execute(
            select(
                SectionModel.id, SectionModel.name, SectionModel.km_start,
                SectionModel.km_end, ST_AsText(SectionModel.center_location).label('center_location'),
                SectionModel.is_active, SectionModel.created_at
            ).where(SectionModel.is_active == is_active)
        )
        sections = result.mappings().all()
        
        return schemas.section.SectionListResponse(
            sections=[schemas.section.SectionResponse(**s) for s in sections]
        )

    async def get_section_by_id(self, section_id: int) -> schemas.section.SectionResponse:
        """Получить участок по ID"""
        result = await self.session.execute(
            select(
                SectionModel.id, SectionModel.name, SectionModel.km_start,
                SectionModel.km_end, ST_AsText(SectionModel.center_location).label('center_location'),
                SectionModel.is_active, SectionModel.created_at
            ).where(SectionModel.id == section_id)
        )
        section = result.mappings().one_or_none()
        
        if not section:
            raise ValueError(f"Section with id {section_id} not found")
            
        return schemas.section.SectionResponse(**section)

    # TRUCKS 

    async def create_truck(self, truck_data: schemas.truck.TruckCreate) -> schemas.truck.TruckResponse:
        """Зарегистрировать новый грузовик"""
        new_truck = TruckModel(**truck_data.model_dump())
        self.session.add(new_truck)
        await self.session.commit()
        await self.session.refresh(new_truck)
        
        return schemas.truck.TruckResponse.model_validate(new_truck, from_attributes=True)

    async def get_all_trucks(self, status: Optional[schemas.enums.TruckStatus] = None) -> schemas.truck.TruckListResponse:
        """Получить список грузовиков с фильтром по статусу"""
        query = select(TruckModel)
        if status:
            query = query.where(TruckModel.status == status)
        
        result = await self.session.execute(query)
        trucks = result.scalars().all()
        
        return schemas.truck.TruckListResponse(
            trucks=[schemas.truck.TruckResponse.model_validate(t, from_attributes=True) for t in trucks]
        )

    # ORDERS 

    async def create_order(self, order_data: schemas.order.OrderCreate) -> schemas.order.OrderResponse:
        """Создать заказ на поставку"""
        new_order = OrderModel(**order_data.model_dump())
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)
        
        return schemas.order.OrderResponse.model_validate(new_order, from_attributes=True)

    async def get_all_orders(self, status: Optional[schemas.enums.OrderStatus] = None) -> schemas.order.OrderListResponse:
        """Получить список заказов"""
        query = select(OrderModel)
        if status:
            query = query.where(OrderModel.status == status)
        
        result = await self.session.execute(query)
        orders = result.scalars().all()
        
        return schemas.order.OrderListResponse(
            orders=[schemas.order.OrderResponse.model_validate(o, from_attributes=True) for o in orders]
        )

    # TRIPS 

    async def create_trip(self, trip_data: schemas.trip.TripCreate) -> schemas.trip.TripResponse:
        """Создать рейс"""
        new_trip = TripModel(**trip_data.model_dump())
        self.session.add(new_trip)
        await self.session.commit()
        await self.session.refresh(new_trip)
        
        return schemas.trip.TripResponse.model_validate(new_trip, from_attributes=True)

    async def get_all_trips(self, order_id: Optional[int] = None) -> schemas.trip.TripListResponse:
        """Получить историю рейсов"""
        query = select(TripModel)
        if order_id:
            query = query.where(TripModel.order_id == order_id)
        
        result = await self.session.execute(query)
        trips = result.scalars().all()
        
        return schemas.trip.TripListResponse(
            trips=[schemas.trip.TripResponse.model_validate(t, from_attributes=True) for t in trips]
        )