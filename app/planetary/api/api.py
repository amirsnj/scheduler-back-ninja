from ninja import Router, Query
from functools import wraps
from typing import List

from .services import PlanetaryClass
from  .schema import PlanetHoursSchema, PlanetRequestQuerySchema


def inject_service(service_cls):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            service = service_cls()   # instantiate correctly
            return func(request, service, *args, **kwargs)
        return wrapper
    return decorator

router = Router(tags=["Planetary"])

@router.get("/", response=List[PlanetHoursSchema])
@inject_service(PlanetaryClass)
def get_hours(request, service: PlanetaryClass, params: PlanetRequestQuerySchema = Query()):
    hours = service.get_planet_hours(
        latitude=params.lat,
        longitude=params.lon,
        city_name=params.city,
        date=params.date
    )
    return [PlanetHoursSchema(**h) for h in hours]