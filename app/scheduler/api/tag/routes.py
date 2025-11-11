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
def get_tag(request, id: int):
    try:
        return TagServices.get_tag_by_id(user_obj=request.auth, tag_id=id)
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str(e))
    

@router.post("/", response={201: TagsSchemaOut})
def add_tag(request, data: TagsSchemaIn):
    try:
        tag = TagServices.create_tag(
            user_obj=request.auth,
            data=data.model_dump()
        )
        return 201, tag
    except Exception as e:
        raise BadRequestError(str(e))
    

@router.put("/{id}", response=TagsSchemaOut)
def update_tag(request, id:int, data: TagsSchemaIn):
    try:
        tag = TagServices.update_tag(
            user_obj=request.auth,
            tag_id=id,
            data=data.model_dump()
        )
        return tag
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str((e)))
    

@router.delete("/{id}", response={204: None})
def delete_tag(request, id: int):
    try:
        TagServices.delete_tag(
            user_obj=request.auth,
            tag_id=id
        )
        return 204, None
    except ObjectDoesNotExist as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise BadRequestError(str((e)))