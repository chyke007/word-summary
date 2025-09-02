from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class TextAnalysisRequest(BaseModel):
    text: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v


class TextAnalysisResponse(BaseModel):
    summary: str
    title: Optional[str]
    topics: List[str]
    sentiment: str
    keywords: List[str]
    created_at: datetime


class SearchRequest(BaseModel):
    keyword: Optional[str] = None
    sentiment: Optional[str] = None
    limit: int = 10


class SearchResponse(BaseModel):
    results: List[TextAnalysisResponse]
    total: int
