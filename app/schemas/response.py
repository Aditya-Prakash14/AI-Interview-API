"""
Response-related Pydantic schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ResponseSubmit(BaseModel):
    """Schema for submitting an interview response"""
    question_id: int
    text_response: Optional[str] = None
    # Note: audio file will be handled separately via file upload


class ScoreBreakdown(BaseModel):
    """Schema for detailed score breakdown"""
    overall_score: int = Field(..., ge=0, le=100)
    content_relevance_score: int = Field(..., ge=0, le=100)
    communication_clarity_score: int = Field(..., ge=0, le=100)
    structure_organization_score: int = Field(..., ge=0, le=100)
    technical_accuracy_score: Optional[int] = Field(None, ge=0, le=100)
    
    # Analysis metrics
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    confidence_indicators: Optional[List[str]] = []
    filler_words_count: int = 0
    word_count: Optional[int] = None
    unique_words_count: Optional[int] = None


class FeedbackDetail(BaseModel):
    """Schema for detailed feedback"""
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    detailed_feedback: Optional[str] = None
    improvement_tips: Optional[str] = None


class ResponseAnalysis(BaseModel):
    """Schema for complete response analysis"""
    response_id: int
    question_id: int
    question_title: str
    original_text: Optional[str] = None
    processed_text: Optional[str] = None
    response_duration_seconds: Optional[float] = None
    transcription_confidence: Optional[float] = None
    
    # Scoring
    scores: ScoreBreakdown
    feedback: FeedbackDetail
    
    # Metadata
    status: str
    processed_at: Optional[datetime] = None
    scoring_model_version: Optional[str] = None
    
    class Config:
        from_attributes = True


class ResponseHistory(BaseModel):
    """Schema for user's response history"""
    responses: List[ResponseAnalysis]
    total_responses: int
    average_overall_score: Optional[float] = None
    improvement_trend: Optional[str] = None  # improving, declining, stable


class ResponseStats(BaseModel):
    """Schema for response statistics"""
    total_responses: int
    average_score: float
    score_distribution: Dict[str, int]  # score ranges and counts
    common_strengths: List[str]
    common_weaknesses: List[str]
    response_time_avg: Optional[float] = None


class BulkResponseAnalysis(BaseModel):
    """Schema for analyzing multiple responses"""
    user_id: int
    responses: List[ResponseAnalysis]
    overall_performance: ResponseStats
    recommendations: List[str]
