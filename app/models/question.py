"""
Question models for interview question management
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table for many-to-many relationship between questions and categories
question_categories = Table(
    'question_categories',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class QuestionCategory(Base):
    """Category model for organizing questions"""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#007bff")  # Hex color for UI
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    questions = relationship("Question", secondary=question_categories, back_populates="categories")
    
    def __repr__(self):
        return f"<QuestionCategory(id={self.id}, name='{self.name}')>"


class Question(Base):
    """Interview question model"""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    difficulty_level = Column(String(20), nullable=False)  # easy, medium, hard
    question_type = Column(String(50), nullable=False)  # behavioral, technical, situational
    expected_duration_minutes = Column(Integer, default=5)
    
    # Scoring criteria
    scoring_criteria = Column(Text, nullable=True)  # JSON string with scoring rubric
    sample_answer = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    
    # Metadata
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    average_score = Column(Integer, nullable=True)  # Average score from responses
    
    # Admin info
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    categories = relationship("QuestionCategory", secondary=question_categories, back_populates="questions")
    responses = relationship("InterviewResponse", back_populates="question")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:50]}...')>"
