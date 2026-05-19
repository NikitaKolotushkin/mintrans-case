#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from geoalchemy2 import Geometry
from app.database import Base
from asphalt_common import *

class TruckModel(Base):
    __tablename__ = "trucks"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), unique=True, nullable=False)
    capacity_tons = Column(Numeric(5, 2), default=20.0)
    
    # Явно указываем имя типа из SQL: truck_status_enum
    status = Column(
        PG_ENUM(TruckStatus, name="truck_status_enum", create_type=False), 
        default=TruckStatus.IDLE
    )
    
    home_plant_id = Column(Integer, ForeignKey("plants.id"))
    created_at = Column(DateTime, server_default=func.now())

class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    
    # Явно указываем имя типа из SQL: order_type_enum
    type = Column(
        PG_ENUM(OrderType, name="order_type_enum", create_type=False), 
        default=OrderType.ASPHALT
    )
    
    plant_id = Column(Integer, ForeignKey("plants.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    ordered_tons = Column(Numeric(8, 2), nullable=False)
    delivered_tons = Column(Numeric(8, 2), default=0)
    
    # Явно указываем имя типа из SQL: order_status_enum
    status = Column(
        PG_ENUM(OrderStatus, name="order_status_enum", create_type=False), 
        default=OrderStatus.PENDING
    )
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PlantModel(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity_per_hour = Column(Numeric(6, 2), nullable=False)
    bunker_capacity = Column(Numeric(6, 2), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class SectionModel(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    start_location = Column(Geometry('POINT', srid=4326), nullable=False)
    end_location = Column(Geometry('POINT', srid=4326), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class TripModel(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    truck_id = Column(Integer, ForeignKey("trucks.id"))
    dispatched_at = Column(DateTime)
    initial_temp_c = Column(Numeric(5, 2))
    redirected_to_section_id = Column(Integer, ForeignKey("sections.id"))
    completed_at = Column(DateTime)
