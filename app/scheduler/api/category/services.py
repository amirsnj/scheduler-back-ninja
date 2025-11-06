from django.db import IntegrityError
from app.scheduler.models import TaskCategory


class CategoryServices:

    @staticmethod
    def get_all_categories(user):
        return TaskCategory.objects.filter(user=user).values("id", "title")
    

    @staticmethod
    def get_catgeory_by_id(user, category_id):
        try:
            return TaskCategory.objects.get(
                pk=category_id,
                user=user
            )
        except TaskCategory.DoesNotExist:
            return None
        

    @staticmethod
    def create_category(user, title: str):
        try:
            category = TaskCategory.objects.create(
                title=title.strip().capitalize(),
                user=user
            )
            
            return category
        except IntegrityError:
            raise ValueError("The category already exists")


    @staticmethod
    def update_category(data_obj, new_data):
        title = new_data.get("title")
        try:
            data_obj.title = title.strip().capitalize()
            data_obj.save()

            return data_obj
        except IntegrityError:
            raise ValueError("The category already exists")


    @staticmethod
    def delete_category(user, id):
        try:
            category = TaskCategory.objects.get(
                pk=id,
                user=user
            )
            category.delete()
            return True
        except TaskCategory.DoesNotExist:
            return False