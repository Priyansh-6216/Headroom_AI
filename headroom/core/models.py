from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Standard message payload based on OpenAI's format."""
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = None
