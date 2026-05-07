from typing import Optional, List, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    tools_used: Optional[List[Any]] = None
    error: Optional[str] = None
    user_id: Optional[str] = None