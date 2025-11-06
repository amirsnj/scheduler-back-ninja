from ninja import Router
from .category.routes import router as CategoryRouter
from .task.routes import router as TaskRouter



router = Router()
router.add_router("categories", CategoryRouter)
router.add_router("tasks", TaskRouter)



