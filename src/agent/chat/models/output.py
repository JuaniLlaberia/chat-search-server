from pydantic import BaseModel, Field

class FollowupOutput(BaseModel):
    questions: list[str] = Field(..., min_length=5, max_length=5, description="Follow up questions")