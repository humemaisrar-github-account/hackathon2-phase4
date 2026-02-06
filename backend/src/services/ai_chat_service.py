import os
from typing import Dict, Any, List
from google.generativeai import configure, GenerativeModel
from ..models.message import Message
from ..models.conversation import Conversation
from ..models.todo import Todo
from .todo_service import TodoService
from .conversation_service import ConversationService
from .message_service import MessageService
from sqlmodel import Session


class AIChatService:
    """
    Service class for handling AI-powered chat interactions.
    Uses Google's Gemini AI through an OpenAI-compatible interface.
    """
    
    def __init__(self):
        # Configure the Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        configure(api_key=api_key)
        self.model = GenerativeModel('gemini-pro')
    
    def process_chat(self, user_input: str, user: Any, session: Session) -> str:
        """
        Process a chat message from the user and return an AI-generated response.
        
        Args:
            user_input: The message from the user
            user: The authenticated user object
            session: Database session
            
        Returns:
            AI-generated response
        """
        # Get the most recent conversation for this user, or create a new one
        conversations, _ = ConversationService.get_user_conversations(session, user, page=1, limit=1)
        if conversations:
            conversation = conversations[0]
        else:
            conversation = ConversationService.create_conversation(session, user)
        
        # Add user message to the conversation
        MessageService.create_message(session, conversation, "user", user_input)
        
        # Get recent messages from the conversation to provide context
        recent_messages, _ = MessageService.get_messages_by_conversation(
            session, conversation, user, page=1, limit=10
        )
        
        # Format messages for the AI model
        formatted_history = []
        for msg in recent_messages:
            formatted_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        
        # Add the current user input
        formatted_history.append({
            "role": "user",
            "parts": [user_input]
        })
        
        # Generate response using the AI model
        try:
            chat = self.model.start_chat(history=formatted_history[:-1])  # Exclude the current input
            response = chat.send_message(user_input)
            ai_response = response.text
        except Exception as e:
            ai_response = f"I'm sorry, I encountered an error processing your request: {str(e)}"
        
        # Add AI response to the conversation
        MessageService.create_message(session, conversation, "assistant", ai_response)
        
        return ai_response
    
    def process_natural_language_todo_command(self, user_input: str, user: Any, session: Session) -> str:
        """
        Process natural language commands related to todo management.
        
        Args:
            user_input: The natural language command from the user
            user: The authenticated user object
            session: Database session
            
        Returns:
            Response indicating the result of the operation
        """
        # Get the most recent conversation for this user, or create a new one
        conversations, _ = ConversationService.get_user_conversations(session, user, page=1, limit=1)
        if conversations:
            conversation = conversations[0]
        else:
            conversation = ConversationService.create_conversation(session, user)
        
        # Add user message to the conversation
        MessageService.create_message(session, conversation, "user", user_input)
        
        # Determine the intent from the user input
        intent = self._determine_intent(user_input.lower())
        
        try:
            if intent == "add":
                response = self._handle_add_todo(user_input, user, session)
            elif intent == "list":
                response = self._handle_list_todos(user_input, user, session)
            elif intent == "complete":
                response = self._handle_complete_todo(user_input, user, session)
            elif intent == "delete":
                response = self._handle_delete_todo(user_input, user, session)
            elif intent == "update":
                response = self._handle_update_todo(user_input, user, session)
            else:
                # If we can't determine the intent, use the general AI model
                response = self._handle_general_query(user_input, conversation, user, session)
        except Exception as e:
            response = f"I'm sorry, I encountered an error processing your request: {str(e)}"
        
        # Add AI response to the conversation
        MessageService.create_message(session, conversation, "assistant", response)
        
        return response
    
    def _determine_intent(self, user_input: str) -> str:
        """
        Determine the intent from the user's input.
        
        Args:
            user_input: The user's input string
            
        Returns:
            The determined intent ('add', 'list', 'complete', 'delete', 'update', or 'other')
        """
        user_input = user_input.lower()
        
        # Keywords for each intent
        add_keywords = ["add", "create", "new", "make", "remember", "remind"]
        list_keywords = ["list", "show", "see", "view", "display", "all", "my"]
        complete_keywords = ["complete", "done", "finish", "mark", "as done", "check"]
        delete_keywords = ["delete", "remove", "cancel", "erase", "get rid of"]
        update_keywords = ["update", "change", "modify", "edit", "rename", "fix"]
        
        # Check for keywords to determine intent
        if any(keyword in user_input for keyword in add_keywords):
            return "add"
        elif any(keyword in user_input for keyword in list_keywords):
            return "list"
        elif any(keyword in user_input for keyword in complete_keywords):
            return "complete"
        elif any(keyword in user_input for keyword in delete_keywords):
            return "delete"
        elif any(keyword in user_input for keyword in update_keywords):
            return "update"
        else:
            return "other"
    
    def _extract_todo_info(self, user_input: str) -> Dict[str, str]:
        """
        Extract todo information from the user's input.
        
        Args:
            user_input: The user's input string
            
        Returns:
            A dictionary with extracted information (title, description)
        """
        # Remove common prefixes
        user_input = user_input.lower()
        for prefix in ["add", "create", "new", "remember", "remind", "me", "to"]:
            user_input = user_input.replace(prefix, "").strip()
        
        # The remaining text is the title
        title = user_input.strip()
        
        return {"title": title, "description": ""}
    
    def _extract_todo_id(self, user_input: str, user: Any, session: Session) -> str:
        """
        Extract the todo ID from the user's input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            The ID of the todo to operate on
        """
        # This is a simplified implementation - in a real app, you'd need more sophisticated parsing
        # For now, we'll just return the ID of the most recently created todo
        todos, _ = TodoService.get_user_todos(session, user, page=1, limit=1)
        if todos:
            return str(todos[0].id)
        return ""
    
    def _handle_add_todo(self, user_input: str, user: Any, session: Session) -> str:
        """
        Handle adding a new todo based on natural language input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            Response message
        """
        # Extract todo information
        todo_info = self._extract_todo_info(user_input)
        
        # Create the todo
        from src.models.todo import TodoCreate
        todo_data = TodoCreate(
            title=todo_info["title"],
            description=todo_info["description"],
            is_completed=False
        )
        
        new_todo = TodoService.create_todo(session, user, todo_data)
        return f"I've added '{new_todo.title}' to your todo list."
    
    def _handle_list_todos(self, user_input: str, user: Any, session: Session) -> str:
        """
        Handle listing todos based on natural language input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            Response message with the list of todos
        """
        # Determine if the user wants all, pending, or completed todos
        status_filter = None
        user_input_lower = user_input.lower()
        if "pending" in user_input_lower or "incomplete" in user_input_lower:
            status_filter = False
        elif "completed" in user_input_lower or "done" in user_input_lower:
            status_filter = True
        
        # Get the todos
        todos, _ = TodoService.get_user_todos(session, user, completed=status_filter, page=1, limit=20)
        
        if not todos:
            if status_filter is False:
                return "You don't have any pending todos right now."
            elif status_filter is True:
                return "You don't have any completed todos right now."
            else:
                return "You don't have any todos right now."
        
        # Format the response
        todo_list = "\n".join([f"- {todo.title}" for todo in todos])
        if status_filter is False:
            return f"Here are your pending todos:\n{todo_list}"
        elif status_filter is True:
            return f"Here are your completed todos:\n{todo_list}"
        else:
            return f"Here are your todos:\n{todo_list}"
    
    def _handle_complete_todo(self, user_input: str, user: Any, session: Session) -> str:
        """
        Handle completing a todo based on natural language input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            Response message
        """
        # Extract the todo ID
        todo_id = self._extract_todo_id(user_input, user, session)
        
        if not todo_id:
            return "I couldn't find a specific todo to mark as complete. Please specify which todo you want to complete."
        
        # Toggle the completion status
        todo = TodoService.toggle_todo_completion(session, todo_id, user)
        status = "completed" if todo.is_completed else "marked as incomplete"
        return f"I've marked '{todo.title}' as {status}."
    
    def _handle_delete_todo(self, user_input: str, user: Any, session: Session) -> str:
        """
        Handle deleting a todo based on natural language input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            Response message
        """
        # Extract the todo ID
        todo_id = self._extract_todo_id(user_input, user, session)
        
        if not todo_id:
            return "I couldn't find a specific todo to delete. Please specify which todo you want to delete."
        
        # Delete the todo
        success = TodoService.delete_todo(session, todo_id, user)
        
        if success:
            return "The todo has been deleted successfully."
        else:
            return "I couldn't delete that todo. It may not exist or you may not have permission to delete it."
    
    def _handle_update_todo(self, user_input: str, user: Any, session: Session) -> str:
        """
        Handle updating a todo based on natural language input.
        
        Args:
            user_input: The user's input string
            user: The authenticated user
            session: Database session
            
        Returns:
            Response message
        """
        # This is a simplified implementation - in a real app, you'd need more sophisticated parsing
        # For now, we'll just update the most recent todo
        todos, _ = TodoService.get_user_todos(session, user, page=1, limit=1)
        
        if not todos:
            return "You don't have any todos to update."
        
        # Extract the new title (simplified)
        new_title = user_input.replace("update", "").replace("change", "").replace("modify", "").strip()
        
        if not new_title:
            return "Please specify what you'd like to change the todo to."
        
        # Update the todo
        from src.models.todo import TodoUpdate
        update_data = TodoUpdate(title=new_title)
        updated_todo = TodoService.update_todo(session, str(todos[0].id), user, update_data)
        
        return f"I've updated the todo to '{updated_todo.title}'."
    
    def _handle_general_query(self, user_input: str, conversation: Conversation, user: Any, session: Session) -> str:
        """
        Handle a general query using the AI model.
        
        Args:
            user_input: The user's input string
            conversation: The current conversation
            user: The authenticated user
            session: Database session
            
        Returns:
            AI-generated response
        """
        # Get recent messages from the conversation to provide context
        recent_messages, _ = MessageService.get_messages_by_conversation(
            session, conversation, user, page=1, limit=10
        )
        
        # Format messages for the AI model
        formatted_history = []
        for msg in recent_messages:
            formatted_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        
        # Add the current user input
        formatted_history.append({
            "role": "user",
            "parts": [user_input]
        })
        
        # Generate response using the AI model
        try:
            chat = self.model.start_chat(history=formatted_history[:-1])  # Exclude the current input
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"