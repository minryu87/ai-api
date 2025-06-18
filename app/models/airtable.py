from pydantic import BaseModel
from typing import List, Optional

class Reply(BaseModel):
    replyText: str

class Comment(BaseModel):
    commentText: str
    replies: List[Reply] = []

class IntegratedText(BaseModel):
    threadText: str
    comments: List[Comment] = []

class AirtableWebhookPayload(BaseModel):
    recordId: str
    tableId: str

class SuccessResponse(BaseModel):
    status: str
    message: str
    threadId: str

class FinalOutput(BaseModel):
    id: str
    threadId: str
    clientName: Optional[str] = None
    channel: Optional[str] = None
    community: Optional[str] = None
    title: Optional[str] = None
    postedAt: Optional[str] = None
    link: Optional[str] = None
    integratedText: IntegratedText
    relevance: Optional[str] = None
    createdAt: Optional[str] = None 