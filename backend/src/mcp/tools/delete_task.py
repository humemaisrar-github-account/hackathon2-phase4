"""
MCP Tool for deleting a task.
"""
from typing import Dict, Any
from mcp.server import server
from ...services.todo_service import TodoService
from sqlmodel import Session
from ...database.database import get_session
from contextlib import next as next_gen


@server.tool(
    "delete_task",
    description="Remove a task from the list",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "integer", "description": "The ID of the task to delete"}
        },
        "required": ["user_id", "task_id"]
    }
)
def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Remove a task from the list.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete
        
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
        
        # Delete the todo
        success = TodoService.delete_todo(session, str(task_id), user)
        
        if success:
            return {
                "task_id": task_id,
                "status": "deleted",
                "title": "Deleted task"  # We can't get the title after deletion
            }
        else:
            return {"error": "Task not found or unauthorized", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        session.close()