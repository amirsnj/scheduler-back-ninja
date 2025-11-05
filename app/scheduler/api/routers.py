from ninja import Router
from .routes.category_router import router as CategoryRouter
from .routes.task_router import router as TaskRouter



router = Router()
router.add_router("categories", CategoryRouter)
router.add_router("tasks", TaskRouter)



