"""
Question-related Pydantic schemas
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = Field(default="#007bff", pattern="^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """Base question schema"""
    title: str = Field(..., min_length=10, max_length=255)
    content: str = Field(..., min_length=20)
    difficulty_level: str = Field(..., pattern="^(easy|medium|hard)$")
    question_type: str = Field(..., pattern="^(behavioral|technical|situational)$")
    expected_duration_minutes: int = Field(default=5, ge=1, le=60)
    scoring_criteria: Optional[str] = None
    sample_answer: Optional[str] = None
    keywords: Optional[str] = None


class QuestionCreate(QuestionBase):
    """Schema for creating a new question"""
    category_ids: List[int] = []


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    content: Optional[str] = Field(None, min_length=20)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    question_type: Optional[str] = Field(None, pattern="^(behavioral|technical|situational)$")
    expected_duration_minutes: Optional[int] = Field(None, ge=1, le=60)
    scoring_criteria: Optional[str] = None
    sample_answer: Optional[str] = None
    keywords: Optional[str] = None
    is_active: Optional[bool] = None
    category_ids: Optional[List[int]] = None


class QuestionResponse(QuestionBase):
    """Schema for question response"""
    id: int
    is_active: bool
    usage_count: int
    average_score: Optional[int] = None
    created_at: datetime
    categories: List[CategoryResponse] = []

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for paginated question list"""
    questions: List[QuestionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class QuestionFilters(BaseModel):
    """Schema for question filtering"""
    category_id: Optional[int] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    question_type: Optional[str] = Field(None, pattern="^(behavioral|technical|situational)$")
    is_active: Optional[bool] = True
    search: Optional[str] = None
