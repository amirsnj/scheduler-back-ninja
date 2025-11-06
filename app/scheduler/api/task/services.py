from app.scheduler.api.schemas import FullTaskSchemaOut
from app.scheduler.models import SubTask, Tag, TaggedItem, Task, TaskCategory
from django.db.models import Prefetch
from django.db import IntegrityError, transaction


class TaskServices:

    @staticmethod
    def get_all_tasks(user_obj):
        tasks = (
            Task.objects.filter(user=user_obj)
            .select_related("category")
            .prefetch_related(
                "subTasks",
                Prefetch(
                    "tagged_items",
                    queryset=TaggedItem.objects.select_related("tag").filter(tag__user=user_obj),
                    to_attr="prefetched_tagged_items"
                )
            )
        )

        full_task_data = [
            {
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
                "subTasks": [
                    {
                        "id": sub_task.id,
                        "title": sub_task.title,
                        "is_completed": sub_task.is_completed
                    } 
                    for sub_task in task.subTasks.all()
                ],
                "tags": [
                    {
                        "id": tagged_item.tag.id,
                        "title": tagged_item.tag.title
                    }
                    for tagged_item in task.prefetched_tagged_items
                ]
            }
            for task in tasks
        ]

        return full_task_data
    

    @staticmethod
    def get_task_by_id(user_obj, task_id):
        try:
            task = (
                Task.objects.filter(user=user_obj, pk=task_id)
                .select_related("category")
                .prefetch_related(
                    "subTasks",
                    Prefetch(
                        "tagged_items",
                        queryset=TaggedItem.objects.select_related("tag").filter(tag__user=user_obj),
                        to_attr="prefetched_tagged_items"
                    )
                ).first()
            )

            if not task:
                raise ValueError(f"Invalid Task ID: {task_id}")

            tags = [
                {
                    "id": tagged_item.tag.id,
                    "title": tagged_item.tag.title
                }
                for tagged_item in task.prefetched_tagged_items
            ]

            sub_tasks = [
                {
                    "id": sub_task.id,
                    "title": sub_task.title,
                    "is_completed": sub_task.is_completed
                }
                for sub_task in task.subTasks.all()
            ]

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
                    "subTasks": sub_tasks,
                    "tags": tags
                }
        except Task.DoesNotExist:
            raise ValueError(f"Invalid Task ID: {task_id}")
    

    @staticmethod
    def create_task(user_obj, task_data: dict):
        category_id = task_data.pop("category", None)
        category_instance = None
        if category_id:
            try:
                category_instance = TaskCategory.objects.get(
                    id=category_id,
                    user=user_obj
                )
            except TaskCategory.DoesNotExist:
                raise ValueError(f"Invalid Category ID: {category_id}")
            
        task = Task.objects.create(
            user=user_obj,
            category=category_instance,
            **task_data
        )

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
                        raise ValueError(f"Invalid category ID: {category_id}")

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

            # Refresh task with all related data
            task.refresh_from_db()
            
            # Fetch related data with select_related/prefetch_related for efficiency
            tagged_items = task.tagged_items.select_related("tag").all()
            subtasks = task.subTasks.all()

            # Build response schema
            return FullTaskSchemaOut(
                id=task.id,
                title=task.title,
                description=task.description,
                category=task.category.id if task.category else None,
                priority_level=task.priority_level,
                scheduled_date=task.scheduled_date,
                dead_line=task.dead_line,
                start_time=task.start_time,
                end_time=task.end_time,
                is_completed=task.is_completed,
                created_at=task.created_at,
                updated_at=task.updated_at,
                tags=[
                    {"id": item.tag.id, "title": item.tag.title} 
                    for item in tagged_items
                ],
                subTasks=[
                    {
                        "id": subtask.id,
                        "title": subtask.title,
                        "is_completed": subtask.is_completed
                    }
                    for subtask in subtasks
                ]
            )

        except ValueError:
            # Re-raise validation errors
            raise
        except IntegrityError as e:
            # Handle database constraint violations
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            # Catch any unexpected errors
            raise ValueError(f"Failed to create task: {str(e)}")
        