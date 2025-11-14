from anydi import Container
from .services import PlanetaryClass

def get_service() -> Container:
    container = Container()

    @container.provider(scope="singleton")
    def service() -> PlanetaryClass:
        return PlanetaryClass()
    
    return container