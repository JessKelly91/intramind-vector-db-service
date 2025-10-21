from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class Document(BaseModel):
    """Base document model for Weaviate collections."""
    
    model_config = ConfigDict()

    id: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class SearchResult(BaseModel):
    """Model for search results."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    content: str
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
