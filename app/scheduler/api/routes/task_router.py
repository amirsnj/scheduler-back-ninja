
from ninja import Router
from typing import List

from app.authentication.api.auth import JWTAuth
from app.core.exceptions import BadRequestError
from app.scheduler.api.schemas import FullTaskSchemaIn, FullTaskSchemaOut, TaskSchemaIn
from app.scheduler.services import TaskServices


router = Router(tags=["Tasks"], auth=JWTAuth())

@router.get("/", response=List[FullTaskSchemaOut])
def get_all_tasks(request):
    return TaskServices.get_all_tasks(user_obj=request.auth)


@router.post("/full-create", response={201: FullTaskSchemaOut})
def full_task_create(request, data: FullTaskSchemaIn):
    try:
        task = TaskServices.create_full_task(user_obj=request.auth, task_data=data.dict())
        return 201, task
    except ValueError as e:
        raise BadRequestError(str(e))
    except Exception as e:
        # Log the error
        raise BadRequestError("Failed to create task")
    

@router.post("/", response={201: FullTaskSchemaOut})
def create_task(request, data: TaskSchemaIn):
    try:
        task = TaskServices.create_task(user_obj=request.auth, task_data=data.dict())
        return 201, task
    except Exception as e:
        raise BadRequestError(str(e))