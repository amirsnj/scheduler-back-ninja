from ninja import Router
from app.authentication.api.auth import JWTAuth
from typing import List
from app.core.exceptions import NotFoundError, BadRequestError
from ..models import TaskCategory
from ..services import CategoryServices, TaskServices
from .schemas import (
    TaskCategorySchema, TaskCategorySchemaIn, FullTaskSchemaIn, FullTaskSchemaOut, TaskSchemaIn, TaskSchemaOut
)


router = Router(tags=["Scheduler"], auth=JWTAuth())


@router.get("/categories", response=List[TaskCategorySchema])
def get_categories(request):
    categories =  CategoryServices.get_all_categories(request.auth)
    return categories


@router.get("/categories/{id}", response=TaskCategorySchema)
def get_category(request, id: int):
    category = CategoryServices.get_catgeory_by_id(request.auth, id)
    if not category:
        raise NotFoundError("Category not found")
    return category


@router.post("/categories", response={201: TaskCategorySchema})
def create_category(request, data: TaskCategorySchemaIn):
    try:
        category = CategoryServices.create_category(
            user=request.auth,
            title=data.title
        )
        return 201, category
    except ValueError as e:
        raise BadRequestError(str(e))
    

@router.put("/categories/{id}", response=TaskCategorySchema)
def update_category(request, id: int, data: TaskCategorySchema):
    try:
        category_object = TaskCategory.objects.get(
            pk=id,
            user=request.auth
        )

        return CategoryServices.update_category(
            data_obj=category_object,
            new_data=data.dict()
        )
    except TaskCategory.DoesNotExist:
        raise NotFoundError("Category not found")
    except ValueError as e:
        raise BadRequestError(str(e))
    

@router.delete("/categories/{id}", response={204: None})
def delete_cateogry(request, id: int):
    result = CategoryServices.delete_category(
        user=request.auth,
        id=id
    )
    if not result:
        raise NotFoundError("Category not found")
    return 204, None


@router.get("/tasks/", response=List[FullTaskSchemaOut])
def get_all_tasks(request):
    return TaskServices.get_all_tasks(user_obj=request.auth)


@router.post("/tasks/full-create", response={201: FullTaskSchemaOut})
def full_task_create(request, data: FullTaskSchemaIn):
    try:
        task = TaskServices.create_full_task(user_obj=request.auth, task_data=data.dict())
        return 201, task
    except ValueError as e:
        raise BadRequestError(str(e))
    except Exception as e:
        # Log the error
        raise BadRequestError("Failed to create task")
    

@router.post("/tasks/", response={201: FullTaskSchemaOut})
def create_task(request, data: TaskSchemaIn):
    try:
        task = TaskServices.create_task(user_obj=request.auth, task_data=data.model_dump())
        return 201, task
    except Exception as e:
        raise BadRequestError(str(e))