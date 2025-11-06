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
    priority_level: PriorityLevel
    scheduled_date: Optional[date] = None
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = None


class TaskUpdateSchema(Schema):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    category: Optional[int]
    priority_level: Optional[PriorityLevel]
    scheduled_date: Optional[date]
    dead_line: Optional[date]
    start_time: Optional[time]
    end_time: Optional[time]
    is_completed: Optional[bool]


class TaskSchemaOut(TaskSchemaIn):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class FullTaskSchemaOut(Schema):
    id: int
    title: str
    description: Optional[str] = ""
    category: Optional[int] = None
    priority_level: PriorityLevel
    scheduled_date: date
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    subTasks: List[SubTaskSchema] = Field(default_factory=list)
    tags: List[TagsSchemaOut] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class FullTaskSchemaIn(Schema):
    title: str
    description: Optional[str] = ""
    category: Optional[int] = None
    priority_level: PriorityLevel = PriorityLevel.medium
    scheduled_date: Optional[date] = None
    dead_line: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_completed: Optional[bool] = None
    tags: List[int] = Field(default_factory=list)
    subTasks: List[SubTaskSchema] = Field(default_factory=list)

    class Config:
        use_enum_values = True