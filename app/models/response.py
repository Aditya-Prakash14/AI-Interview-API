"""
Response models for storing interview responses and scores
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InterviewResponse(Base):
    """Model for storing user responses to interview questions"""
    
    __tablename__ = "interview_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    # Response content
    original_text = Column(Text, nullable=True)  # Original transcribed text
    processed_text = Column(Text, nullable=True)  # Cleaned/processed text
    audio_file_path = Column(String(500), nullable=True)
    response_duration_seconds = Column(Float, nullable=True)
    
    # Processing metadata
    transcription_confidence = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question", back_populates="responses")
    scores = relationship("ResponseScore", back_populates="response", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InterviewResponse(id={self.id}, user_id={self.user_id}, question_id={self.question_id})>"


class ResponseScore(Base):
    """Model for storing detailed scoring of interview responses"""
    
    __tablename__ = "response_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("interview_responses.id"), nullable=False)
    
    # Overall scores (0-100)
    overall_score = Column(Integer, nullable=False)
    content_relevance_score = Column(Integer, nullable=False)
    communication_clarity_score = Column(Integer, nullable=False)
    structure_organization_score = Column(Integer, nullable=False)
    technical_accuracy_score = Column(Integer, nullable=True)
    
    # Detailed analysis
    strengths = Column(JSON, nullable=True)  # List of identified strengths
    weaknesses = Column(JSON, nullable=True)  # List of areas for improvement
    suggestions = Column(JSON, nullable=True)  # Specific improvement suggestions
    
    # NLP Analysis results
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    confidence_indicators = Column(JSON, nullable=True)  # Words/phrases indicating confidence
    filler_words_count = Column(Integer, default=0)
    word_count = Column(Integer, nullable=True)
    unique_words_count = Column(Integer, nullable=True)
    
    # Feedback text
    detailed_feedback = Column(Text, nullable=True)
    improvement_tips = Column(Text, nullable=True)
    
    # Scoring metadata
    scoring_model_version = Column(String(50), nullable=True)
    scoring_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("InterviewResponse", back_populates="scores")
    
    def __repr__(self):
        return f"<ResponseScore(id={self.id}, response_id={self.response_id}, overall_score={self.overall_score})>"
