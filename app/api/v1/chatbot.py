from fastapi import APIRouter, Depends, HTTPException

from app.middleware.authenticate import authenticate
from app.models.user import User
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.services.chatbot import get_chatbot

router = APIRouter(tags=["chatbot"])

@router.post("/chat")
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(authenticate)
):
    """
    Chat with the office chatbot

    Args:
        request: Chat request containing message and optional user_id
    """
    try:
        chatbot = get_chatbot()

        # Use current user's ID if not provided
        user_id = str(current_user.id)

        result = await chatbot.chat(request.message, user_id)

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

@router.post("/chat/clear-memory")
async def clear_chat_memory(
    current_user: User = Depends(authenticate)
):
    """
    Clear conversation memory for the authenticated user
    """
    try:
        chatbot = get_chatbot()
        user_id = str(current_user.id)
        await chatbot.clear_memory(user_id)
        return {"message": "Chat memory cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@router.get("/chat/history")
async def get_chat_history(current_user: User = Depends(authenticate)):
    """
    Get conversation history for the authenticated user
    """
    try:
        chatbot = get_chatbot()
        user_id = str(current_user.id)
        history = await chatbot.get_conversation_history(user_id)
        return {"history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")