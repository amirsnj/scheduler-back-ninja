
from ninja import Router
from typing import List
from django.core.exceptions import ObjectDoesNotExist

from app.authentication.api.auth import JWTAuth
from app.core.exceptions import BadRequestError, NotFoundError
from app.scheduler.api.schemas import FullTaskSchemaIn, FullTaskSchemaOut, TaskSchemaIn, TaskUpdateSchema
from .services import TaskServices
from django.db import connection


router = Router(tags=["Tasks"], auth=JWTAuth())


@router.get("/", response=List[FullTaskSchemaOut])
def get_all_tasks(request):
    tasks = TaskServices.get_all_tasks(user_obj=request.auth)
    print(f"\033[34mqueries: {len(connection.queries)}\033[0m")
    for q in connection.queries:
        print(q["sql"], "\n")

    return tasks


@router.post("/full-create/", response={201: FullTaskSchemaOut})
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


@router.get("/{id}", response=FullTaskSchemaOut)
def get_task(request, id:int):
    try:
        return TaskServices.get_task_by_id(user_obj=request.auth, task_id=id)
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str)
    

@router.put("/{id}", response=FullTaskSchemaOut)
def update_task_put(request, id: int, data: TaskSchemaIn):
    try:
        return TaskServices.update_task(
            user_obj=request.auth,
            task_id=id,
            data=data.model_dump()
        )
    
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    
    except Exception as e:
        raise BadRequestError(str(e))
    

@router.patch("/{id}", response=FullTaskSchemaOut)
def update_task_patch(request, id: int, data: TaskUpdateSchema):
    try:
        return TaskServices.update_task_partial(
            user_obj=request.auth,
            task_id=id,
            data=data.model_dump(exclude_unset=True)
        )
    
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    
    except Exception as e:
        raise BadRequestError(str(e))


@router.delete("/{id}", response={204: None})
def delete_task(request, id: int):
    try: 
        TaskServices.delete_task(user_obj=request.auth, task_id=id)
        return 204, None
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str(e))
    

@router.put("/{id}/update/", response=FullTaskSchemaOut)
def full_task_update(request, id: int, data: FullTaskSchemaIn):
    try:
        return TaskServices.update_full_task(
            user_obj=request.auth,
            task_id=id,
            data=data.model_dump()
        )
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str(e))