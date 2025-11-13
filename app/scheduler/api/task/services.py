from typing import List
from django.db.models import Prefetch, QuerySet
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone

from app.scheduler.api.schemas import FullTaskSchemaOut, PriorityLevel
from app.scheduler.models import SubTask, Tag, TaggedItem, Task, TaskCategory
from .utils import validate_times, validate_dates

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
            category_instance = TaskServices._validate_category(
                user_obj=user_obj,
                category_id=category_id
            )
            
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
                    category_instance = TaskServices._validate_category(
                        user_obj=user_obj,
                        category_id=category_id
                    )

                #validate times
                scheduled_date = task_data.get("scheduled_date") or timezone.now().date()
                dead_line = task_data.get("dead_line")
                validate_dates(scheduled_date=scheduled_date, dead_line=dead_line)

                start_time = task_data.get("start_time")
                end_time = task_data.get("end_time")
                validate_times(start_time=start_time, end_time=end_time)

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
    def update_full_task(user_obj, task_id: int, data: dict):
        task = TaskServices._fetch_tasks(user_obj=user_obj).filter(pk=task_id).first()
        if not task:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found")

        tags = data.pop("tags", None)
        sub_tasks = data.pop("subTasks", None)

        with transaction.atomic():

            for attr, value in data.items():
                if attr == "category":
                    value = TaskServices._validate_category(user_obj=user_obj, category_id=value)
                setattr(task, attr, value)
            task.save()

            if tags is not None:
                TaskServices.__update_full_task_tags(task=task, new_tags=tags)

            if sub_tasks is not None:
                TaskServices.__update_full_task_subtasks(task=task, new_subtasks=sub_tasks)
            
        task.refresh_from_db()
        if tags is not None:
            del task.prefetched_tagged_items
            task.prefetched_tagged_items = list(TaggedItem.objects.select_related("tag").filter(task=task, tag__user=user_obj))

        return TaskServices._serialize_task(task)


    @staticmethod
    def __update_full_task_tags(task, new_tags):
        current_tags = set(
            TaggedItem.objects.filter(task=task).values_list("tag_id", flat=True)
        )
        new_tags = set(new_tags)

        tags_to_remove = current_tags - new_tags
        if tags_to_remove:
            TaggedItem.objects.filter(task=task, tag_id__in=tags_to_remove).delete()

        tags_to_add = new_tags - current_tags
        if tags_to_add:
            tagged_items = [
                TaggedItem(tag_id=tag_id, task=task) for tag_id in tags_to_add
            ]
            TaggedItem.objects.bulk_create(tagged_items)

    @staticmethod
    def __update_full_task_subtasks(task, new_subtasks):
        current_subtasks = {
            st.id: st for st in SubTask.objects.filter(parent_task=task)
        }

        subtasks_to_create = []
        subtasks_to_update = []
        updated_ids = set()

        for subtask_data in new_subtasks:
            subtask_id = subtask_data.get("id")

            if subtask_id and subtask_id in current_subtasks:
                subtask_instance = current_subtasks[subtask_id]
                subtask_instance.title = subtask_data.get("title", subtask_instance.title)
                subtask_instance.is_completed = subtask_data.get("is_completed", subtask_instance.is_completed)

                subtasks_to_update.append(subtask_instance)
                updated_ids.add(subtask_id)
            else:
                subtasks_to_create.append(
                    SubTask(
                        parent_task=task,
                        title=subtask_data.get("title", ""),
                        is_completed=subtask_data.get("is_completed", False)
                    )
                )
        
        subtasks_to_delete = set(current_subtasks.keys()) - updated_ids
        if subtasks_to_delete:
            SubTask.objects.filter(id__in=subtasks_to_delete).delete()

        if subtasks_to_update:
            SubTask.objects.bulk_update(subtasks_to_update, ["title", "is_completed"])

        if subtasks_to_create:
            SubTask.objects.bulk_create(subtasks_to_create)


    @staticmethod
    def update_task(user_obj, task_id: int, data: dict):
        task = TaskServices._fetch_tasks(user_obj=user_obj).filter(pk=task_id).first()
        if not task:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found")
        
        title = data.get("title")
        if not title:
            raise ValidationError("Title is required for full update")
        
        if len(title.strip()) <= 0:
            raise ValidationError("Title cannot be empty")
        
        priority_level = data.get("priority_level", PriorityLevel.medium)
        if isinstance(priority_level, PriorityLevel):
            priority_level = priority_level.value

        category_id = data.get("category")
        category = None
        if category_id:
            category = TaskServices._validate_category(
                user_obj=user_obj,
                category_id=category_id
            )

        scheduled_date = data.get("scheduled_date") or timezone.now().date()
        dead_line = data.get("dead_line")
        validate_dates(scheduled_date, dead_line)

        start_time = data.get("start_time")
        end_time = data.get("end_time")
        validate_times(start_time, end_time)


        task.title = title.strip()
        task.description = data.get("description", "")
        task.category = category
        task.priority_level = priority_level
        task.scheduled_date = scheduled_date
        task.dead_line = dead_line
        task.start_time = start_time
        task.end_time = end_time
        task.is_completed = data.get("is_completed", False)

        task.save()

        return TaskServices._serialize_task(task)
    

    @staticmethod
    def update_task_partial(user_obj, task_id: int, data: dict):
        task = TaskServices._fetch_tasks(user_obj=user_obj).filter(pk=task_id).first()
        if not task:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found")
        
        for field, value in data.items():
            if field == "category":
                value = TaskServices._validate_category(user_obj=user_obj, category_id=value)

            setattr(task, field, value)

        validate_dates(
            scheduled_date=task.scheduled_date,
            dead_line=task.dead_line
        )

        validate_times(
            start_time=task.start_time,
            end_time=task.end_time
        )

        task.save()

        return TaskServices._serialize_task(task)

        

    @staticmethod
    def delete_task(user_obj, task_id):
        task = TaskServices._fetch_tasks(user_obj=user_obj).filter(pk=task_id).first()
        if not task:
            raise ObjectDoesNotExist(f"Task with ID {task_id} not found")
        
        task.delete()

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
    
    @staticmethod
    def _validate_category(user_obj, category_id):
        try:
            category = TaskCategory.objects.get(pk=category_id, user=user_obj)
            return category
        except TaskCategory.DoesNotExist:
            raise ValidationError(f"Category with ID {category_id} not found.")
        