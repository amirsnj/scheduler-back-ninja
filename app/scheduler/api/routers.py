from ninja import Router
from .category.routes import router as CategoryRouter
from .task.routes import router as TaskRouter
from .tag.routes import router as TagRouter



router = Router()
router.add_router("categories", CategoryRouter)
router.add_router("tasks", TaskRouter)
router.add_router("tags", TagRouter)



