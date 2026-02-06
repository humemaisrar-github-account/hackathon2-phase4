from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from src.models.message import Message, MessageCreate
from src.models.conversation import Conversation
from src.models.user import User
from src.api.middleware.error_handler import AuthorizationError, NotFoundError


class MessageService:
    """Service class for handling message-related operations."""

    @staticmethod
    def create_message(
        session: Session,
        conversation: Conversation,
        role: str,
        content: str
    ) -> Message:
        """
        Create a new message in a conversation.

        Args:
            session: Database session
            conversation: The conversation to add the message to
            role: The role of the message ('user' or 'assistant')
            content: The content of the message

        Returns:
            The created Message object
        """
        message_data = MessageCreate(
            conversation_id=conversation.id,
            role=role,
            content=content
        )
        
        db_message = Message(
            conversation_id=message_data.conversation_id,
            role=message_data.role,
            content=message_data.content
        )
        
        session.add(db_message)
        session.commit()
        session.refresh(db_message)

        # Update the conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        return db_message

    @staticmethod
    def get_messages_by_conversation(
        session: Session,
        conversation: Conversation,
        user: User,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Message], int]:
        """
        Get all messages for a specific conversation with pagination.

        Args:
            session: Database session
            conversation: The conversation whose messages to retrieve
            user: The user requesting the messages
            page: Page number for pagination
            limit: Number of items per page

        Returns:
            Tuple of (list of messages, total count)

        Raises:
            AuthorizationError: If user doesn't own the conversation
        """
        # Verify the user owns the conversation
        if conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to access messages in this conversation")

        # Build query for messages in the conversation
        query = select(Message).where(Message.conversation_id == conversation.id)

        # Calculate offset for pagination
        offset = (page - 1) * limit

        # Execute query with pagination
        messages = session.exec(query.offset(offset).limit(limit)).all()

        # Get total count
        count_query = select(Message).where(Message.conversation_id == conversation.id)
        total_count = session.exec(count_query).all().__len__()

        return messages, total_count

    @staticmethod
    def get_message_by_id(session: Session, message_id: str, user: User) -> Message:
        """
        Get a specific message by ID and verify user ownership of the conversation.

        Args:
            session: Database session
            message_id: ID of the message to retrieve
            user: The user requesting the message

        Returns:
            The Message object

        Raises:
            NotFoundError: If message doesn't exist
            AuthorizationError: If user doesn't own the conversation containing the message
        """
        db_message = session.get(Message, message_id)

        if not db_message:
            raise NotFoundError("Message", message_id)

        # Get the conversation to verify user ownership
        conversation = session.get(Conversation, db_message.conversation_id)
        if not conversation or conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to access this message")

        return db_message

    @staticmethod
    def update_message(session: Session, message_id: str, user: User, content: str) -> Message:
        """
        Update a message if the user owns the conversation it belongs to.

        Args:
            session: Database session
            message_id: ID of the message to update
            user: The user updating the message
            content: The new content for the message

        Returns:
            The updated Message object

        Raises:
            NotFoundError: If message doesn't exist
            AuthorizationError: If user doesn't own the conversation containing the message
        """
        db_message = session.get(Message, message_id)

        if not db_message:
            raise NotFoundError("Message", message_id)

        # Get the conversation to verify user ownership
        conversation = session.get(Conversation, db_message.conversation_id)
        if not conversation or conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to update this message")

        # Update message with new content
        db_message.content = content
        db_message.updated_at = datetime.utcnow()

        session.add(db_message)
        session.commit()
        session.refresh(db_message)

        return db_message

    @staticmethod
    def delete_message(session: Session, message_id: str, user: User) -> bool:
        """
        Delete a message if the user owns the conversation it belongs to.

        Args:
            session: Database session
            message_id: ID of the message to delete
            user: The user deleting the message

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If message doesn't exist
            AuthorizationError: If user doesn't own the conversation containing the message
        """
        db_message = session.get(Message, message_id)

        if not db_message:
            raise NotFoundError("Message", message_id)

        # Get the conversation to verify user ownership
        conversation = session.get(Conversation, db_message.conversation_id)
        if not conversation or conversation.user_id != str(user.id):
            raise AuthorizationError("Not authorized to delete this message")

        session.delete(db_message)
        session.commit()

        return True