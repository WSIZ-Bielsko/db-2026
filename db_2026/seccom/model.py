from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Message(BaseModel):
    id: UUID
    sender_key: str
    recipient_key: str
    content: str
    created_at: datetime
    group_id: UUID | None = None

class Group(BaseModel):
    id: UUID
    name: str

class GroupUser(BaseModel):
    group_id: UUID
    user_key: str