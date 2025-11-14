from datetime import datetime
from typing import Optional
from ninja import Schema, FilterSchema


class PlanetHoursSchema(Schema):
    hour: int
    planet: str
    start_time: datetime
    end_time: datetime


class PlanetRequestQuerySchema(FilterSchema):
    lat: float
    lon: float
    city: str
    date: Optional[str] = None
