from datetime import date, datetime, time
from typing import List, Optional
from ninja import Field, Schema
from enum import Enum


class TaskCategorySchema(Schema):
    id: int
    title: str


class TaskCategorySchemaIn(Schema):
    title: str


class SubTaskSchema(Schema):
    id: Optional[int] = None
    title: str
    is_completed: bool


class TagsSchemaIn(Schema):
    title: str


class TagsSchemaOut(Schema):
    id: int
    title: str


class PriorityLevel(str, Enum):
    low = "L"
    medium = "M"
    high = "H"


class TaskSchemaIn(Schema):
    title: str
    description: Optional[str] = ""
    category: Optional[int] = None
    priority_level: Optional[PriorityLevel] = PriorityLevel.medium
    scheduled_date: Optional[date] = None
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = False


class TaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[int] = None
    priority_level: Optional[PriorityLevel] = None
    scheduled_date: Optional[date] = None
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = None


class TaskSchemaOut(Schema):
    id: int
    title: str
    description: str
    category: Optional[int] = None
    priority_level: PriorityLevel
    scheduled_date: date
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime



class FullTaskSchemaOut(TaskSchemaOut):
    subTasks: List[SubTaskSchema] = Field(default_factory=list)
    tags: List[TagsSchemaOut] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class FullTaskSchemaIn(TaskSchemaIn):
    tags: List[int] = Field(default_factory=list)
    subTasks: List[SubTaskSchema] = Field(default_factory=list)

    class Config:
        use_enum_values = True
