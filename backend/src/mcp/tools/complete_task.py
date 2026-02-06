"""
MCP Tool for completing a task.
"""
from typing import Dict, Any
from mcp.server import server
from ...services.todo_service import TodoService
from sqlmodel import Session
from ...database.database import get_session
from contextlib import next as next_gen


@server.tool(
    "complete_task",
    description="Mark a task as complete",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "integer", "description": "The ID of the task to complete"}
        },
        "required": ["user_id", "task_id"]
    }
)
def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Mark a task as complete.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete
        
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
        
        # Toggle the completion status of the todo
        updated_todo = TodoService.toggle_todo_completion(session, str(task_id), user)
        
        return {
            "task_id": updated_todo.id,
            "status": "completed",
            "title": updated_todo.title,
            "completed": updated_todo.is_completed
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        session.close()