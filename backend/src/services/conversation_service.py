from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from src.models.conversation import Conversation, ConversationCreate
from src.models.user import User
from src.models.message import Message
from src.api.middleware.error_handler import AuthorizationError, NotFoundError


class ConversationService:
    """Service class for handling conversation-related operations."""

    @staticmethod
    def create_conversation(session: Session, user: User) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            session: Database session
            user: The user creating the conversation

        Returns:
            The created Conversation object
        """
        db_conversation = Conversation(
            user_id=str(user.id)
        )
        
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)

        return db_conversation

    @staticmethod
    def get_user_conversations(
        session: Session,
        user: User,
        page: int = 1,
        limit: int = 10
    ) -> tuple[List[Conversation], int]:
        """
        Get all conversations for a specific user with pagination.

        Args:
            session: Database session
            user: The user whose conversations to retrieve
            page: Page number for pagination
            limit: Number of items per page

        Returns:
            Tuple of (list of conversations, total count)
        """
        # Build query for user's conversations
        query = select(Conversation).where(Conversation.user_id == str(user.id))

        # Calculate offset for pagination
        offset = (page - 1) * limit

        # Execute query with pagination
        conversations = session.exec(query.offset(offset).limit(limit)).all()

        # Get total count
        count_query = select(Conversation).where(Conversation.user_id == str(user.id))
        total_count = session.exec(count_query).all().__len__()

        return conversations, total_count

    @staticmethod
    def get_conversation_by_id(session: Session, conversation_id: str, user: User) -> Conversation:
        """
        Get a specific conversation by ID and verify user ownership.

        Args:
            session: Database session
            conversation_id: ID of the conversation to retrieve
            user: The user requesting the conversation

        Returns:
            The Conversation object

        Raises:
            NotFoundError: If conversation doesn't exist
            AuthorizationError: If user doesn't own the conversation
        """
        db_conversation = session.get(Conversation, conversation_id)

        if not db_conversation:
            raise NotFoundError("Conversation", conversation_id)

        if db_conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to access this conversation")

        return db_conversation

    @staticmethod
    def delete_conversation(session: Session, conversation_id: str, user: User) -> bool:
        """
        Delete a conversation if the user owns it.

        Args:
            session: Database session
            conversation_id: ID of the conversation to delete
            user: The user deleting the conversation

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If conversation doesn't exist
            AuthorizationError: If user doesn't own the conversation
        """
        db_conversation = session.get(Conversation, conversation_id)

        if not db_conversation:
            raise NotFoundError("Conversation", conversation_id)

        if db_conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to delete this conversation")

        # Also delete all associated messages
        messages = session.exec(select(Message).where(Message.conversation_id == conversation_id)).all()
        for message in messages:
            session.delete(message)

        session.delete(db_conversation)
        session.commit()

        return True