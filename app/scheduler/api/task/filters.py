from ninja import FilterSchema
from typing import Optional

class TaskFilterSchema(FilterSchema):
    scheduled_date: Optional[str] = None
