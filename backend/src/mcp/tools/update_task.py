"""
MCP Tool for updating a task.
"""
from typing import Dict, Any
from mcp.server import server
from ...services.todo_service import TodoService
from ...models.todo import TodoUpdate
from sqlmodel import Session
from ...database.database import get_session
from contextlib import next as next_gen


@server.tool(
    "update_task",
    description="Modify task title or description",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "integer", "description": "The ID of the task to update"},
            "title": {"type": "string", "description": "New title for the task (optional)"},
            "description": {"type": "string", "description": "New description for the task (optional)"}
        },
        "required": ["user_id", "task_id"]
    }
)
def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> Dict[str, Any]:
    """
    Modify task title or description.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        
    Returns:
        Dictionary with task details
    """
    # Get a database session
    session_gen = get_session()
    session: Session = next_gen(session_gen)
    
    try:
        # Find the user by ID
        from ...models.user import User
        user = session.get(User, user_id)
        if not user:
            return {"error": "User not found", "status": "failed"}
        
        # Prepare update data
        update_data = TodoUpdate()
        if title is not None:
            update_data.title = title
        if description is not None:
            update_data.description = description
        
        # Update the todo
        updated_todo = TodoService.update_todo(session, str(task_id), user, update_data)
        
        return {
            "task_id": updated_todo.id,
            "status": "updated",
            "title": updated_todo.title,
            "description": updated_todo.description
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        session.close()