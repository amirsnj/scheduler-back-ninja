from ninja import NinjaAPI
from ninja.parser import Parser
from app.authentication.api.routers import router as auth_router
from app.scheduler.api.routers import router as scheduler_router


api = NinjaAPI(
    title="Schduler API",
    version="1.0.0",
    description="RESTful API"
)

api.add_router("/auth", auth_router)
api.add_router("/schedule", scheduler_router)