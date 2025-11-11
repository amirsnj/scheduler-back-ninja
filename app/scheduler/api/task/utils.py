from django.core.exceptions import ValidationError

def validate_dates(scheduled_date, dead_line):
    if dead_line:
        if dead_line < scheduled_date:
            raise ValidationError("Deadline cannot be in the past")
        
        if scheduled_date and dead_line < scheduled_date:
            raise ValidationError("Deadline cannot be before scheduled date")
        

def validate_times(start_time, end_time):
    if start_time and end_time:
        if end_time <= start_time:
            raise ValidationError("End time msut be after start time")