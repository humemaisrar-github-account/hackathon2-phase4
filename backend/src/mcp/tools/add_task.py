"""
MCP Tool for adding a new task.
"""
from typing import Dict, Any
from mcp.server import server
from ...services.todo_service import TodoService
from ...models.todo import TodoCreate
from sqlmodel import Session
from ...database.database import get_session
from contextlib import next as next_gen


@server.tool(
    "add_task",
    description="Create a new task for a user",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "title": {"type": "string", "description": "The title of the task"},
            "description": {"type": "string", "description": "The description of the task"}
        },
        "required": ["user_id", "title"]
    }
)
def add_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for a user.
    
    Args:
        user_id: The ID of the user
        title: The title of the task
        description: The description of the task (optional)
        
    Returns:
        Dictionary with the created task details
    """
    # Get a database session
    session_gen = get_session()
    session: Session = next_gen(session_gen)
    
    try:
        # Create the todo data
        todo_data = TodoCreate(
            title=title,
            description=description,
            is_completed=False
        )
        
        # Find the user by ID (we'll need to create a mock user object for this)
        from ...models.user import User
        user = session.get(User, user_id)
        if not user:
            return {"error": "User not found", "status": "failed"}
        
        # Create the todo
        new_todo = TodoService.create_todo(session, user, todo_data)
        
        return {
            "task_id": new_todo.id,
            "status": "created",
            "title": new_todo.title,
            "description": new_todo.description,
            "completed": new_todo.is_completed
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        session.close()