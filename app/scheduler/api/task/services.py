from typing import List
from app.scheduler.api.schemas import FullTaskSchemaOut
from app.scheduler.models import SubTask, Tag, TaggedItem, Task, TaskCategory
from django.db.models import Prefetch, QuerySet
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist


class TaskServices:

    @staticmethod
    def get_all_tasks(user_obj):
        tasks = TaskServices._fetch_tasks(user_obj)
        return [TaskServices._serialize_task(task) for task in tasks]
    

    @staticmethod
    def get_task_by_id(user_obj, task_id):
        task = TaskServices._fetch_tasks(user_obj=user_obj)\
        .filter(pk=task_id).first()

        if not task:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found for user {user_obj.id}")
        
        return TaskServices._serialize_task(task)
    

    @staticmethod
    def create_task(user_obj, task_data: dict) -> dict:
        category_id = task_data.pop("category", None)
        category_instance = None

        if category_id:
            try:
                category_instance = TaskCategory.objects.get(
                    id=category_id,
                    user=user_obj
                )
            except TaskCategory.DoesNotExist:
                raise ObjectDoesNotExist(f"Category with ID {category_id}")
            
        task = Task.objects.create(
            user=user_obj,
            category=category_instance,
            **task_data
        )

        return TaskServices._serializer_task_basic(task)


    @staticmethod
    def create_full_task(user_obj, task_data: dict):
        tags = task_data.pop("tags", [])
        sub_tasks = task_data.pop("subTasks", [])

        try:
            with transaction.atomic():
                # Validate tags exist and belong to user
                if tags:
                    valid_tags = Tag.objects.filter(
                        id__in=tags, 
                        user=user_obj
                    ).values_list('id', flat=True)
                    
                    if len(valid_tags) != len(tags):
                        invalid_tags = set(tags) - set(valid_tags)
                        raise ValueError(f"Invalid tag IDs: {invalid_tags}")

                # Validate and fetch category if provided
                category_id = task_data.pop('category', None)
                category_instance = None
                if category_id:
                    try:
                        category_instance = TaskCategory.objects.get(
                            id=category_id, 
                            user=user_obj
                        )
                    except TaskCategory.DoesNotExist:
                        raise ObjectDoesNotExist(f"Category with ID {category_id} not found")

                # Create the main task
                task = Task.objects.create(
                    user=user_obj, 
                    category=category_instance,
                    **task_data
                )

                # Create tagged items if tags provided
                if tags:
                    tagged_items = [
                        TaggedItem(tag_id=tag_id, task=task) 
                        for tag_id in tags
                    ]
                    TaggedItem.objects.bulk_create(tagged_items)

                # Create subtasks if provided
                if sub_tasks:
                    subtask_objects = [
                        SubTask(
                            parent_task=task,
                            title=sub_task.get('title'),
                            is_completed=sub_task.get('is_completed', False)
                        )
                        for sub_task in sub_tasks
                    ]
                    SubTask.objects.bulk_create(subtask_objects)

            
            # Fetch related data with select_related/prefetch_related for efficiency
            tagged_items = task.tagged_items.select_related("tag").all()
            subtasks = task.subTasks.all()

            task_response = TaskServices._serializer_task_basic(task)
            task_response["subTasks"] = TaskServices._serialize_subtasks(subtasks)
            task_response["tags"] = TaskServices._serizlie_tags(tagged_items)

            return task_response            


        except (ValueError, ObjectDoesNotExist):
            raise
        except IntegrityError as e:
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create task: {str(e)}")
        

    @staticmethod
    def update_task(user_obj, task_id, new_obj):
        try:
            data_obj = Task.objects.get(pk=task_id, user=user_obj)

            for field, value in new_obj.items():
                if field == "category":
                    category = TaskCategory.objects.filter(pk=value, user=user_obj).first()
                    if not category:
                        raise ObjectDoesNotExist(f"Task Category with ID {value} not found.")
                    setattr(data_obj, field, category)
                else:
                    setattr(data_obj, field, value)

            data_obj.save()
            return TaskServices._serializer_task_basic(data_obj)
        
        except Task.DoesNotExist:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found")

    @staticmethod
    def _fetch_tasks(user_obj) -> QuerySet:
        tagged_items_prefetch = Prefetch(
            "tagged_items",
            queryset=TaggedItem.objects.select_related("tag").filter(tag__user=user_obj),
            to_attr="prefetched_tagged_items"
        )

        return (
            Task.objects
            .filter(user=user_obj)
            .select_related("category")
            .prefetch_related("subTasks", tagged_items_prefetch)
        )
    
    @staticmethod
    def _serialize_task(task: 'Task') -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "category": task.category.id if task.category else None,
            "priority_level": task.priority_level,
            "scheduled_date": task.scheduled_date,
            "dead_line": task.dead_line,
            "start_time": task.start_time,
            "end_time": task.end_time,
            "is_completed": task.is_completed,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "subTasks": TaskServices._serialize_subtasks(task.subTasks.all()),
            "tags": TaskServices._serizlie_tags(task.prefetched_tagged_items)
        }
    
    @staticmethod
    def _serializer_task_basic(task: 'Task') -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "category": task.category.id if task.category else None,
            "priority_level": task.priority_level,
            "scheduled_date": task.scheduled_date,
            "dead_line": task.dead_line,
            "start_time": task.start_time,
            "end_time": task.end_time,
            "is_completed": task.is_completed,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "subTasks": [],
            "tags": []
        }
    
    @staticmethod
    def _serialize_subtasks(subtasks: QuerySet) -> List[dict]:
        return [
            {
                "id": subtask.id,
                "title": subtask.title,
                "is_completed": subtask.is_completed
            }
            for subtask in subtasks
        ]
    
    @staticmethod
    def _serizlie_tags(tagged_items: list) -> List[dict]:
        return [
            {
                "id": tagged_item.tag.id,
                "title": tagged_item.tag.title
            }
            for tagged_item in tagged_items
        ]
        