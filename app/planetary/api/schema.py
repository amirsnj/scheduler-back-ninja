from datetime import time
from typing import Optional
from ninja import Schema, FilterSchema


class PlanetHoursSchema(Schema):
    hour: int
    planet: str
    start_time: time
    end_time: time


class PlanetRequestQuerySchema(FilterSchema):
    lat: int
    lon: int
    city: str
    date: Optional[str] = None
