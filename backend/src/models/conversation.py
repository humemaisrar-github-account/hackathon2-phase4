from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ConversationBase(SQLModel):
    user_id: str = Field(foreign_key="user.id")


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(SQLModel):
    pass


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a chat conversation between a user and the AI assistant.
    """
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)