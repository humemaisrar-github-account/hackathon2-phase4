from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Any
from src.database.database import get_session
from src.api.middleware.auth_middleware import get_current_user
from src.models.user import User
from src.services.ai_chat_service import AIChatService

router = APIRouter()

@router.post("/{user_id}/chat")
def chat_with_ai(
    user_id: str,
    request: Dict[str, Any],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Main chat endpoint for interacting with the AI assistant.
    
    Args:
        user_id: ID of the user chatting with the AI
        request: Request containing the user's message
        session: Database session
        current_user: Authenticated user
        
    Returns:
        Dictionary with AI's response
    """
    # Verify the authenticated user matches the requested user_id
    current_user_id_str = str(current_user.id)
    user_id_str = str(user_id)
    if current_user_id_str != user_id_str:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's chat"
        )
    
    # Get the user's message from the request
    user_message = request.get("message", "")
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    try:
        # Create the AI chat service
        ai_service = AIChatService()
        
        # Process the natural language command
        response = ai_service.process_natural_language_todo_command(
            user_input=user_message,
            user=current_user,
            session=session
        )
        
        return {
            "response": response,
            "user_id": user_id_str,
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )