from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Document(BaseModel):
    """Base document model for Weaviate collections."""

    id: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchResult(BaseModel):
    """Model for search results."""

    id: str
    content: str
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
