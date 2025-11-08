from typing import List
from ninja import Router
from django.core.exceptions import ObjectDoesNotExist

from app.authentication.api.auth import JWTAuth
from app.core.exceptions import NotFoundError, BadRequestError
from app.scheduler.api.schemas import TagsSchemaIn, TagsSchemaOut
from .services import TagServices


router = Router(tags=["Tags"], auth=JWTAuth())

@router.get("/", response=List[TagsSchemaOut])
def get_tags(request):
    return TagServices.get_all_tags(user_obj=request.auth)


@router.get("/{id}", response=TagsSchemaOut)
def get_tag(request, tag: int):
    try:
        return TagServices.get_tag_by_id(user_obj=request.auth, tag_id=tag)
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str(e))
    

@router.post("/", response=TagsSchemaOut)
def add_tag(request, data: TagsSchemaIn):
    pass