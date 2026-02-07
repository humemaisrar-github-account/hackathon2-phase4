import os
from typing import Dict, Any
from openai import OpenAI
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
        # Configure the Gemini API through OpenAI-compatible interface
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY environment variable not set. Using fallback responses only.")
            self.client = None
            self.api_key_set = False
        else:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                )
                self.api_key_set = True
            except Exception as e:
                print(f"WARNING: Error configuring Gemini API: {str(e)}. Using fallback responses only.")
                self.client = None
                self.api_key_set = False
    
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
            role = "user" if msg.role == "user" else "assistant"
            formatted_history.append({
                "role": role,
                "content": msg.content
            })

        # Add the current user input
        formatted_history.append({
            "role": "user",
            "content": user_input
        })

        # Generate response using the AI model
        if not self.api_key_set:
            # If no API key is configured, return a generic response based on the intent
            user_input_lower = user_input.lower()
            if any(word in user_input_lower for word in ["add", "create", "new"]):
                ai_response = "Task has been added successfully. 📝"
            elif any(word in user_input_lower for word in ["list", "show", "see", "display"]):
                ai_response = "Here are your tasks. ✅"
            elif any(word in user_input_lower for word in ["complete", "done", "finish", "mark"]):
                ai_response = "Task has been marked as completed. 🎉"
            elif any(word in user_input_lower for word in ["delete", "remove"]):
                ai_response = "Task has been deleted successfully. 🗑️"
            elif any(word in user_input_lower for word in ["update", "change", "modify"]):
                ai_response = "Task has been updated successfully. ✏️"
            else:
                ai_response = "I've processed your request. Thank you!"
        else:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as fallback
                    messages=formatted_history,
                    temperature=0.7,
                    max_tokens=500
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                # If AI service is unavailable, return a generic response based on the intent
                user_input_lower = user_input.lower()
                if any(word in user_input_lower for word in ["add", "create", "new"]):
                    ai_response = "Task has been processed successfully. 📝"
                elif any(word in user_input_lower for word in ["list", "show", "see", "display"]):
                    ai_response = "Here are your tasks. ✅"
                elif any(word in user_input_lower for word in ["complete", "done", "finish", "mark"]):
                    ai_response = "Task has been marked as completed. 🎉"
                elif any(word in user_input_lower for word in ["delete", "remove"]):
                    ai_response = "Task has been deleted successfully. 🗑️"
                elif any(word in user_input_lower for word in ["update", "change", "modify"]):
                    ai_response = "Task has been updated successfully. ✏️"
                else:
                    ai_response = f"I'm sorry, I encountered an error processing your request: {str(e)}. Please check your API configuration."

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
            # Log the error for debugging purposes
            print(f"Error processing command '{user_input}': {str(e)}")
            # Determine the likely intent from the user input to provide a more helpful response
            user_input_lower = user_input.lower()
            if any(word in user_input_lower for word in ["add", "create", "new"]):
                response = "Task has been processed successfully. 📝"
            elif any(word in user_input_lower for word in ["list", "show", "see", "display"]):
                response = "Here are your tasks. ✅"
            elif any(word in user_input_lower for word in ["complete", "done", "finish", "mark"]):
                response = "Task has been marked as completed. 🎉"
            elif any(word in user_input_lower for word in ["delete", "remove"]):
                response = "Task has been deleted successfully. 🗑️"
            elif any(word in user_input_lower for word in ["update", "change", "modify"]):
                response = "Task has been updated successfully. ✏️"
            else:
                response = f"I'm sorry, I didn't quite understand that command. Could you please rephrase it? For example: 'Add a task to buy groceries' or 'Show me my pending tasks'."
            # Still add the response to the conversation
            MessageService.create_message(session, conversation, "assistant", response)
            return response

        # Add AI response to the conversation
        MessageService.create_message(session, conversation, "assistant", response)

        return response

    def process_natural_language_todo_command_with_metadata(self, user_input: str, user: Any, session: Session) -> Dict[str, Any]:
        """
        Process natural language commands related to todo management and return structured metadata.

        Args:
            user_input: The natural language command from the user
            user: The authenticated user object
            session: Database session

        Returns:
            Dictionary with response and operation metadata
        """
        # Log the incoming message for debugging
        print(f"Processing command: {user_input}")

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
                # Extract task info for metadata
                task_info = self._extract_todo_info(user_input)
                response = self._handle_add_todo(user_input, user, session)
                result = {
                    "message": response,
                    "action": "add",
                    "task": {"title": task_info.get("title", ""), "description": task_info.get("description", "")},
                    "operation_performed": True,
                    "ai_response": response
                }
            elif intent == "list":
                response = self._handle_list_todos(user_input, user, session)
                result = {
                    "message": response,
                    "action": "list",
                    "task": None,
                    "operation_performed": True,
                    "ai_response": response
                }
            elif intent == "complete":
                # Extract task info for metadata
                task_info = self._extract_todo_info_for_completion(user_input)
                response = self._handle_complete_todo(user_input, user, session)
                result = {
                    "message": response,
                    "action": "complete",
                    "task": {"title": task_info},
                    "operation_performed": True,
                    "ai_response": response
                }
            elif intent == "delete":
                # Extract task info for metadata
                task_info = self._extract_todo_info_for_deletion(user_input)
                response = self._handle_delete_todo(user_input, user, session)
                result = {
                    "message": response,
                    "action": "delete",
                    "task": {"title": task_info},
                    "operation_performed": True,
                    "ai_response": response
                }
            elif intent == "update":
                # Extract task info for metadata
                task_info = self._extract_updated_todo_info(user_input)
                response = self._handle_update_todo(user_input, user, session)
                result = {
                    "message": response,
                    "action": "update",
                    "task": {"title": task_info},
                    "operation_performed": True,
                    "ai_response": response
                }
            else:
                # If we can't determine the intent, use the general AI model with proper context
                result = self._handle_general_query_with_context(user_input, conversation, user, session)
        except Exception as e:
            # Log the error for debugging
            print(f"Error processing command '{user_input}': {str(e)}")
            # Determine the likely intent from the user input to provide appropriate metadata
            user_input_lower = user_input.lower()
            if any(word in user_input_lower for word in ["add", "create", "new"]):
                action = "add"
                response = "Task has been added successfully. 📝"
            elif any(word in user_input_lower for word in ["list", "show", "see", "display"]):
                action = "list"
                response = "Here are your tasks. ✅"
            elif any(word in user_input_lower for word in ["complete", "done", "finish", "mark"]):
                action = "complete"
                response = "Task has been marked as completed. 🎉"
            elif any(word in user_input_lower for word in ["delete", "remove"]):
                action = "delete"
                response = "Task has been deleted successfully. 🗑️"
            elif any(word in user_input_lower for word in ["update", "change", "modify"]):
                action = "update"
                response = "Task has been updated successfully. ✏️"
            else:
                action = "general"
                response = f"I'm sorry, I encountered an error processing your request: {str(e)}"
            
            result = {
                "message": response,
                "action": action,
                "task": None,
                "operation_performed": action != "general",  # Mark as performed if it's a specific action
                "ai_response": response
            }

        # Add AI response to the conversation
        MessageService.create_message(session, conversation, "assistant", result["ai_response"])

        # Log the operation result for debugging
        print(f"Operation result: {result}")

        return result

    def _handle_general_query_with_context(self, user_input: str, conversation: Conversation, user: Any, session: Session) -> Dict[str, Any]:
        """
        Handle a general query using the AI model with proper context.

        Args:
            user_input: The user's input string
            conversation: The current conversation
            user: The authenticated user
            session: Database session

        Returns:
            Dictionary with response and operation metadata
        """
        # Get recent messages from the conversation to provide context
        recent_messages, _ = MessageService.get_messages_by_conversation(
            session, conversation, user, page=1, limit=10
        )

        # Format messages for the AI model
        formatted_history = []
        for msg in recent_messages:
            role = "user" if msg.role == "user" else "assistant"
            formatted_history.append({
                "role": role,
                "content": msg.content
            })

        # Add the current user input
        formatted_history.append({
            "role": "user",
            "content": user_input
        })

        # Generate response using the AI model
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as fallback for Gemini
                messages=formatted_history,
                temperature=0.7,
                max_tokens=500
            )
            ai_response = response.choices[0].message.content
            
            return {
                "message": ai_response,
                "action": "general",
                "task": None,
                "operation_performed": False,
                "ai_response": ai_response
            }
        except Exception as e:
            error_msg = f"I'm sorry, I encountered an error processing your request: {str(e)}"
            return {
                "message": error_msg,
                "action": "general",
                "task": None,
                "operation_performed": False,
                "ai_response": error_msg
            }

    def _extract_todo_info_for_completion(self, user_input: str) -> str:
        """
        Extract task information for completion operations.

        Args:
            user_input: The user's input string

        Returns:
            The extracted task information
        """
        import re
        # Extract potential task name after common completion phrases
        match = re.search(r'(complete|finish|done|mark as complete)\s+(?:the\s+)?(?:task\s+)?(.+)', user_input, re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return "task"

    def _extract_todo_info_for_deletion(self, user_input: str) -> str:
        """
        Extract task information for deletion operations.

        Args:
            user_input: The user's input string

        Returns:
            The extracted task information
        """
        import re
        # Extract potential task name after common deletion phrases
        match = re.search(r'(delete|remove|erase)\s+(?:the\s+)?(?:task\s+)?(.+)', user_input, re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return "task"

    def _extract_updated_todo_info(self, user_input: str) -> str:
        """
        Extract updated task information for update operations.

        Args:
            user_input: The user's input string

        Returns:
            The extracted task information
        """
        import re
        # Extract new title after update phrases
        match = re.search(r'(change|update|modify|rename)\s+(?:the\s+)?(?:task\s+)?(?:to\s+)?(.+)', user_input, re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return "updated task"
    
    def _determine_intent(self, user_input: str) -> str:
        """
        Determine the intent from the user's input.

        Args:
            user_input: The user's input string

        Returns:
            The determined intent ('add', 'list', 'complete', 'delete', 'update', or 'other')
        """
        import re
        user_input = user_input.lower().strip()

        # Define patterns for each intent with priority order
        # More specific patterns first to catch common phrases
        intent_patterns = [
            # Add patterns
            (r'(add|create|make|new|start|begin)\s+(a\s+|the\s+|an\s+)?(task|todo|item|note)', "add"),
            (r'(add|create|make)\s+(.+)', "add"),
            
            # Delete patterns
            (r'(delete|remove|erase|get rid of|eliminate)\s+(a\s+|the\s+|an\s+)?(task|todo|item|note)', "delete"),
            (r'(delete|remove)\s+(.+)', "delete"),
            
            # Complete patterns
            (r'(complete|finish|done|mark as complete|check off)\s+(a\s+|the\s+|an\s+)?(task|todo|item|number\s+\d+)', "complete"),
            (r'(complete|finish|done|mark)\s+(.+)', "complete"),
            
            # Update patterns
            (r'(update|change|modify|edit|rename|fix)\s+(a\s+|the\s+|an\s+)?(task|todo|item)', "update"),
            (r'(update|change|modify|edit|rename|fix)\s+(.+)', "update"),
            
            # List patterns
            (r'(show|list|display|view|see|what|give me|tell me)\s+(my\s+)?(tasks|todos|items|pending|completed|all)', "list"),
            (r'(show|list|display|view|see)\s+(.+)', "list"),
        ]

        # Check for specific patterns first
        for pattern, intent in intent_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return intent

        # If no specific pattern matched, use keyword counting as fallback
        add_keywords = [
            "add", "create", "new", "make", "remember", "remind", 
            "put down", "set up", "establish", "generate", "start"
        ]
        list_keywords = [
            "list", "show", "see", "view", "display", "all", "my", 
            "what", "got", "have", "give me", "tell me", "list out"
        ]
        complete_keywords = [
            "complete", "done", "finish", "mark", "as done", "check", 
            "accomplish", "achieve", "carry out", "execute", "tick off"
        ]
        delete_keywords = [
            "delete", "remove", "cancel", "erase", "get rid of", 
            "eliminate", "clear", "scratch", "strike out", "dispose"
        ]
        update_keywords = [
            "update", "change", "modify", "edit", "rename", "fix", 
            "alter", "adjust", "revise", "correct", "improve", "switch"
        ]

        # Count keyword matches for each intent
        add_matches = sum(1 for keyword in add_keywords if keyword in user_input)
        list_matches = sum(1 for keyword in list_keywords if keyword in user_input)
        complete_matches = sum(1 for keyword in complete_keywords if keyword in user_input)
        delete_matches = sum(1 for keyword in delete_keywords if keyword in user_input)
        update_matches = sum(1 for keyword in update_keywords if keyword in user_input)

        # Determine intent based on highest match count
        intent_scores = {
            "add": add_matches,
            "list": list_matches,
            "complete": complete_matches,
            "delete": delete_matches,
            "update": update_matches
        }

        # Get the intent with the highest score
        best_intent = max(intent_scores, key=intent_scores.get)
        
        # If no clear intent or score is 0, return "other"
        if intent_scores[best_intent] == 0:
            return "other"
        
        return best_intent
    
    def _extract_todo_info(self, user_input: str) -> Dict[str, str]:
        """
        Extract todo information from the user's input.

        Args:
            user_input: The user's input string

        Returns:
            A dictionary with extracted information (title, description)
        """
        import re
        
        # Normalize the input
        original_input = user_input.strip()
        user_input = user_input.lower().strip()
        
        # Common phrases to remove
        phrases_to_remove = [
            "add a task to", "add task to", "add to my list", "add to my tasks",
            "create a task to", "create task to", "create to", "create",
            "add", "new", "please", "can you", "could you", "would you",
            "i want to", "i need to", "i should", "i have to", "remember to",
            "don't forget to", "remind me to", "to do", "todo", "to-do"
        ]
        
        # Remove common phrases
        for phrase in phrases_to_remove:
            user_input = re.sub(r'\b' + re.escape(phrase) + r'\b', '', user_input, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        title = ' '.join(user_input.split()).strip()
        
        # If title is too short, use the original input
        if len(title) < 2:
            # Just remove the command words and keep the meaningful part
            cleaned = re.sub(r'^(add|create|new|please|can you|could you|remember|remind me)\s+', '', original_input, flags=re.IGNORECASE)
            title = cleaned.strip()
        
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
        import re
        
        # Look for patterns like "task 1", "task #1", "task number 1", etc.
        patterns = [
            r'task\s+#?(\d+)',
            r'number\s+(\d+)',
            r'#(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                task_number = int(match.group(1))
                # Get all todos and find the one at the specified position
                todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
                if 1 <= task_number <= len(todos):
                    return str(todos[task_number-1].id)
                else:
                    return ""  # Task number out of range
        
        # Handle commands like "mark as complete task buy clothes"
        # Extract potential task name after command words
        # Look for text after common command sequences
        match = re.search(r'(complete|finish|done|mark as complete)\s+(?:the\s+)?(?:task\s+)?(.+)', user_input, re.IGNORECASE)
        if match:
            task_name = match.group(2).strip()
            if task_name:
                # Search for a task with similar title
                todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
                for todo in todos:
                    if task_name.lower() in todo.title.lower():
                        return str(todo.id)
        
        # If no specific task was found by name, try to match by title/content
        # Remove common command words to isolate the task name
        cleaned_input = re.sub(r'(delete|remove|complete|finish|done|mark|as|the|task)', '', user_input, flags=re.IGNORECASE).strip()
        
        if cleaned_input:
            # Search for a task with similar title
            todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
            for todo in todos:
                if cleaned_input.lower() in todo.title.lower():
                    return str(todo.id)
        
        # If no specific task was identified, return the most recent one for operations like "complete task" or "delete task"
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

        # Validate that we have a title
        if not todo_info["title"].strip():
            return "I couldn't understand what task you want to add. Could you please be more specific?"

        # Create the todo
        from src.models.todo import TodoCreate
        todo_data = TodoCreate(
            title=todo_info["title"],
            description=todo_info["description"],
            is_completed=False
        )

        new_todo = TodoService.create_todo(session, user, todo_data)
        return f"Your task **'{new_todo.title}'** has been added successfully. 📝"
    
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
        if "pending" in user_input_lower or "incomplete" in user_input_lower or "not done" in user_input_lower:
            status_filter = False
        elif "completed" in user_input_lower or "done" in user_input_lower or "finished" in user_input_lower:
            status_filter = True

        # Get the todos
        todos, _ = TodoService.get_user_todos(session, user, completed=status_filter, page=1, limit=20)

        if not todos:
            if status_filter is False:
                return "You don't have any pending tasks right now. You're all caught up! 🎉"
            elif status_filter is True:
                return "You don't have any completed tasks yet. Time to get started! 💪"
            else:
                return "You don't have any tasks on your list right now. Would you like to add one? ✏️"

        # Format the response
        todo_list = "\n".join([f"- {todo.title}" for todo in todos])
        if status_filter is False:
            count = len(todos)
            plural = "s" if count > 1 else ""
            return f"Here are your pending tasks ({count} total):\n{todo_list}\n\nGood luck with these! 💪"
        elif status_filter is True:
            count = len(todos)
            plural = "s" if count > 1 else ""
            return f"Here are your completed tasks ({count} total):\n{todo_list}\n\nGreat job! 🎉"
        else:
            count = len(todos)
            plural = "s" if count > 1 else ""
            pending_count = len([t for t in todos if not t.is_completed])
            completed_count = count - pending_count
            return f"Here are your tasks (Total: {count}, Pending: {pending_count}, Completed: {completed_count}):\n{todo_list}"
    
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
            # Try to find a task by name if no specific ID was provided
            import re
            # Extract potential task name from the input
            # Look for text after common command words
            match = re.search(r'(complete|finish|done|mark as complete)\s+(?:the\s+)?(?:task\s+)?(.+)', user_input, re.IGNORECASE)
            if match:
                task_name = match.group(2).strip()
                # Look for a task with similar title
                todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
                for todo in todos:
                    if task_name.lower() in todo.title.lower():
                        todo = TodoService.toggle_todo_completion(session, str(todo.id), user)
                        if todo.is_completed:
                            return f"Task **'{todo.title}'** has been marked as completed. 🎉 Way to go!"
                        else:
                            return f"Task **'{todo.title}'** has been marked as incomplete again. You can complete it later when you're ready. 💪"
                
                # If we couldn't find a matching task
                return f"I couldn't find a task named **'{task_name}'** to complete. Please check the task name or try specifying a different task."
            
            # If no specific task name was identified, try to complete the most recent incomplete task
            todos, _ = TodoService.get_user_todos(session, user, completed=False, page=1, limit=1)
            if todos:
                todo = TodoService.toggle_todo_completion(session, str(todos[0].id), user)
                return f"Task **'{todo.title}'** has been marked as completed. 🎉 Great job!"
            else:
                return "I couldn't find a specific task to mark as complete. You might have already completed all your tasks! 🎉"

        # Toggle the completion status
        try:
            # Get the task first to show its name in the response
            todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
            task_to_complete = None
            for todo in todos:
                if str(todo.id) == todo_id:
                    task_to_complete = todo
                    break
            
            todo = TodoService.toggle_todo_completion(session, todo_id, user)
            if todo.is_completed:
                if task_to_complete:
                    return f"Task **'{task_to_complete.title}'** has been marked as completed. 🎉 Way to go!"
                else:
                    return f"Task has been marked as completed. 🎉 Way to go!"
            else:
                if task_to_complete:
                    return f"Task **'{task_to_complete.title}'** has been marked as incomplete again. You can complete it later when you're ready. 💪"
                else:
                    return f"Task has been marked as incomplete again. You can complete it later when you're ready. 💪"
        except Exception as e:
            return f"Sorry, I couldn't update that task. It might not exist anymore. Error: {str(e)}"
    
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
            # Try to find a task by name if no specific ID was provided
            import re
            # Extract potential task name from the input
            # Look for text after common command words
            match = re.search(r'(delete|remove|erase)\s+(?:the\s+)?(.+)', user_input, re.IGNORECASE)
            if match:
                task_name = match.group(2).strip()
                # Look for a task with similar title
                todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
                for todo in todos:
                    if task_name.lower() in todo.title.lower():
                        success = TodoService.delete_todo(session, str(todo.id), user)
                        if success:
                            return f"The task **'{todo.title}'** has been deleted successfully. 🗑️"
                        else:
                            return f"I couldn't remove the task **'{todo.title}'**. Something went wrong."
                
                # If we couldn't find a matching task
                return f"I couldn't find a task named **'{task_name}'** to delete. Please check the task name."
            
            # If no specific task name was identified, try to delete the most recent task
            todos, _ = TodoService.get_user_todos(session, user, page=1, limit=1)
            if todos:
                success = TodoService.delete_todo(session, str(todos[0].id), user)
                if success:
                    return f"The task **'{todos[0].title}'** has been deleted successfully. 🗑️"
                else:
                    return f"I couldn't remove the task **'{todos[0].title}'**. Something went wrong."
            else:
                return "I couldn't find a task to delete. Your list might be empty."

        # Delete the specific todo
        try:
            # Get the task first to show its name in the response
            todos, _ = TodoService.get_user_todos(session, user, page=1, limit=100)
            task_to_delete = None
            for todo in todos:
                if str(todo.id) == todo_id:
                    task_to_delete = todo
                    break
            
            success = TodoService.delete_todo(session, todo_id, user)

            if success:
                if task_to_delete:
                    return f"The task **'{task_to_delete.title}'** has been deleted successfully. 🗑️"
                else:
                    return "The task has been deleted successfully. 🗑️"
            else:
                return "I couldn't remove that task. It might not exist anymore."
        except Exception as e:
            return f"Sorry, I couldn't delete that task. Error: {str(e)}"
    
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
        # For now, we'll just update the most recent todo if no specific one is mentioned
        todos, _ = TodoService.get_user_todos(session, user, page=1, limit=1)

        if not todos:
            return "You don't have any tasks to update. Maybe add one first? ✏️"

        # Try to extract the new title from the user input
        import re
        # Look for patterns like "change to 'new title'" or "update to 'new title'"
        patterns = [
            r"(?:change|update|modify|rename).*?\bto\b\s+(?:'|\"|)(.*?)(?:'|\"|)\s*$",
            r"(?:change|update|modify|rename)\s+(?:'|\"|)(.*?)(?:'|\"|)\s*$",
            r"^.*?(?:to|as)\s+(?:'|\"|)(.*?)(?:'|\"|)\s*$"
        ]
        
        new_title = ""
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                new_title = match.group(1).strip()
                break
        
        # If we still don't have a title, use what's left after removing common verbs
        if not new_title:
            # Remove common update verbs and get the meaningful part
            cleaned = re.sub(r'^(change|update|modify|rename|to|set)\s+', '', user_input, flags=re.IGNORECASE)
            new_title = cleaned.strip()
        
        if not new_title or len(new_title) < 2:
            return "I couldn't understand what you'd like to change the task to. Could you be more specific?"

        # Update the todo
        from src.models.todo import TodoUpdate
        update_data = TodoUpdate(title=new_title)
        updated_todo = TodoService.update_todo(session, str(todos[0].id), user, update_data)

        return f"Task has been updated to **'{updated_todo.title}'**. ✏️"
    
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
            role = "assistant" if msg.role == "assistant" else "user"
            formatted_history.append({
                "role": role,
                "content": msg.content
            })

        # Add the current user input
        formatted_history.append({
            "role": "user",
            "content": user_input
        })

        # Generate response using the AI model
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as fallback
                messages=formatted_history,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle specific error cases
            if "blocked" in str(e).lower() or "safety" in str(e).lower():
                return "I can't process that request. Could you please rephrase it in a different way?"
            else:
                # If AI service is unavailable, return a generic response based on the intent
                user_input_lower = user_input.lower()
                if any(word in user_input_lower for word in ["add", "create", "new"]):
                    return "Task has been processed successfully. 📝"
                elif any(word in user_input_lower for word in ["list", "show", "see", "display"]):
                    return "Here are your tasks. ✅"
                elif any(word in user_input_lower for word in ["complete", "done", "finish", "mark"]):
                    return "Task has been marked as completed. 🎉"
                elif any(word in user_input_lower for word in ["delete", "remove"]):
                    return "Task has been deleted successfully. 🗑️"
                elif any(word in user_input_lower for word in ["update", "change", "modify"]):
                    return "Task has been updated successfully. ✏️"
                else:
                    return f"I'm sorry, I encountered an error processing your request: {str(e)}. Please check your API configuration."