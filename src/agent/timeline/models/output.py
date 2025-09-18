from datetime import date as date_type
from pydantic import BaseModel, Field

class TimelineEvent(BaseModel):
    start_date: str = Field(..., description="Start date of the event")
    end_date: str | None = Field(None, description="End date if the event spans a range")
    title: str = Field(..., description="Title/Label of the event")
    content: str = Field(..., description="Description of the event (What happend?)")

class TimelineOutput(BaseModel):
    events: list[TimelineEvent] = Field(..., min_length=6, max_length=20, description="List of events that belong to the timeline")

class EvaluateTimelineOutput(BaseModel):
    score: float = Field(..., description="Score from 0-1 evaluating the timeline")
    improvements: str = Field(..., description="Improvements to make to the timeline")