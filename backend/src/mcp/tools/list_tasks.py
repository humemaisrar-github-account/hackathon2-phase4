"""
MCP Tool for listing tasks.
"""
from typing import Dict, Any, List
from mcp.server import server
from ...services.todo_service import TodoService
from sqlmodel import Session
from ...database.database import get_session
from contextlib import next as next_gen


@server.tool(
    "list_tasks",
    description="Retrieve tasks from the list",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter tasks by status (default: all)"
            }
        },
        "required": ["user_id"]
    }
)
def list_tasks(user_id: str, status: str = "all") -> Dict[str, Any]:
    """
    Retrieve tasks from the list.
    
    Args:
        user_id: The ID of the user
        status: Filter tasks by status ("all", "pending", "completed")
        
    Returns:
        Dictionary with an array of task objects
    """
    # Get a database session
    session_gen = get_session()
    session: Session = next_gen(session_gen)
    
    try:
        # Convert status to boolean for the service
        completed_filter = None
        if status == "pending":
            completed_filter = False
        elif status == "completed":
            completed_filter = True
        # If status is "all", keep completed_filter as None
        
        # Find the user by ID
        from ...models.user import User
        user = session.get(User, user_id)
        if not user:
            return {"error": "User not found", "status": "failed"}
        
        # Get the todos
        todos, _ = TodoService.get_user_todos(session, user, completed=completed_filter, page=1, limit=100)
        
        # Format the tasks
        task_list = []
        for todo in todos:
            task_list.append({
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.is_completed
            })
        
        return {
            "tasks": task_list,
            "count": len(task_list)
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        session.close()