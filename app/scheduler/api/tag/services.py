from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist

from app.scheduler.models import Tag


class TagServices:

    @staticmethod
    def get_all_tags(user_obj):
        tags = TagServices._fetch_tags(user_obj=user_obj)
        return [TagServices._serialize_tags(tag) for tag in tags]
    
    @staticmethod
    def get_tag_by_id(user_obj, tag_id):
        tag = TagServices._fetch_tags(user_obj=user_obj).filter(pk=tag_id).first()

        if not tag:
            raise ObjectDoesNotExist(f"Tag with ID {tag_id} not found")
        
        return TagServices._serialize_tags(tag)
    
    @staticmethod
    def create_tag(user_obj, data):
        pass




    @staticmethod
    def _fetch_tags(user_obj) -> QuerySet:
        return Tag.objects.filter(user=user_obj)
    
    @staticmethod
    def _serialize_tags(tag: 'Tag') -> dict:
        return {
            "id": tag.id,
            "title": tag.title
        }