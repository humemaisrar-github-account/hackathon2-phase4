from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class MessageBase(SQLModel):
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(SQLModel):
    content: Optional[str] = None


class Message(MessageBase, table=True):
    """
    Message model representing a single message in a conversation.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)