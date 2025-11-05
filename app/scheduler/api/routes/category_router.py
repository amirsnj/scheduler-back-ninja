from ninja import Router
from app.authentication.api.auth import JWTAuth
from typing import List

from app.core.exceptions import BadRequestError, NotFoundError
from app.scheduler.api.schemas import TaskCategorySchema, TaskCategorySchemaIn
from app.scheduler.models import TaskCategory
from app.scheduler.services import CategoryServices



router = Router(tags=["Categories"], auth=JWTAuth())


@router.get("/", response=List[TaskCategorySchema])
def get_categories(request):
    categories =  CategoryServices.get_all_categories(request.auth)
    return categories


@router.get("/{id}", response=TaskCategorySchema)
def get_category(request, id: int):
    category = CategoryServices.get_catgeory_by_id(request.auth, id)
    if not category:
        raise NotFoundError("Category not found")
    return category


@router.post("/", response={201: TaskCategorySchema})
def create_category(request, data: TaskCategorySchemaIn):
    try:
        category = CategoryServices.create_category(
            user=request.auth,
            title=data.title
        )
        return 201, category
    except ValueError as e:
        raise BadRequestError(str(e))
    

@router.put("/{id}", response=TaskCategorySchema)
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
    

@router.delete("/{id}", response={204: None})
def delete_cateogry(request, id: int):
    result = CategoryServices.delete_category(
        user=request.auth,
        id=id
    )
    if not result:
        raise NotFoundError("Category not found")
    return 204, None