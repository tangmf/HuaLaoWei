from pydantic import BaseModel
from typing import Optional, List

class ChatbotInput(BaseModel):
    text: Optional[str] = None
    audio: Optional[str] = None
    documents: Optional[List[str]] = None
