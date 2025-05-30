"""
Interview API routes for submitting responses and getting questions
"""
import os
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.response import InterviewResponse, ResponseScore
from app.schemas.response import ResponseSubmit, ResponseAnalysis, ResponseHistory
from app.schemas.question import QuestionResponse, QuestionFilters
from app.utils.security import get_current_user
from app.utils.validators import validate_audio_file, validate_text_input, clean_text_input
from app.services.audio_processor import AudioProcessor
from app.services.nlp_scorer import NLPScorer
from app.services.feedback_generator import FeedbackGenerator
from app.services.question_manager import QuestionManager

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get("/questions", response_model=List[QuestionResponse])
async def get_interview_questions(
    count: int = 5,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get random interview questions for practice"""
    
    question_manager = QuestionManager(db)
    
    if category_id or difficulty or question_type:
        # Use filtered approach
        filters = QuestionFilters(
            category_id=category_id,
            difficulty_level=difficulty,
            question_type=question_type,
            is_active=True
        )
        questions, _ = question_manager.get_questions(filters, page=1, per_page=count)
    else:
        # Get random questions
        questions = question_manager.get_random_questions(
            count=count,
            difficulty_level=difficulty,
            question_type=question_type
        )
    
    if not questions:
        raise HTTPException(
            status_code=404,
            detail="No questions found matching the criteria"
        )
    
    return questions


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific question by ID"""
    
    question_manager = QuestionManager(db)
    question = question_manager.get_question(question_id)
    
    if not question or not question.is_active:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.post("/submit-text", response_model=ResponseAnalysis)
async def submit_text_response(
    response_data: ResponseSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a text-based interview response"""
    
    # Validate input
    if not response_data.text_response:
        raise HTTPException(
            status_code=400,
            detail="Text response is required"
        )
    
    validate_text_input(response_data.text_response)
    
    # Get the question
    question = db.query(Question).filter(Question.id == response_data.question_id).first()
    if not question or not question.is_active:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Clean the text input
    cleaned_text = clean_text_input(response_data.text_response)
    
    # Create response record
    interview_response = InterviewResponse(
        user_id=current_user.id,
        question_id=response_data.question_id,
        original_text=response_data.text_response,
        processed_text=cleaned_text,
        status="processing"
    )
    
    db.add(interview_response)
    db.commit()
    db.refresh(interview_response)
    
    # Process response in background
    background_tasks.add_task(
        process_text_response,
        interview_response.id,
        cleaned_text,
        question.content,
        question.question_type
    )
    
    # Update question usage
    question_manager = QuestionManager(db)
    question_manager.increment_question_usage(response_data.question_id)
    
    # Return initial response (will be updated by background task)
    return ResponseAnalysis(
        response_id=interview_response.id,
        question_id=question.id,
        question_title=question.title,
        original_text=response_data.text_response,
        processed_text=cleaned_text,
        status="processing",
        scores={
            "overall_score": 0,
            "content_relevance_score": 0,
            "communication_clarity_score": 0,
            "structure_organization_score": 0,
            "technical_accuracy_score": None,
            "sentiment_score": 0.0,
            "confidence_indicators": 0,
            "filler_words_count": 0,
            "word_count": len(cleaned_text.split()),
            "unique_words_count": len(set(cleaned_text.lower().split()))
        },
        feedback={
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "detailed_feedback": "Processing your response...",
            "improvement_tips": "Please wait while we analyze your response."
        }
    )


@router.post("/submit-audio", response_model=ResponseAnalysis)
async def submit_audio_response(
    question_id: int = Form(...),
    audio_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an audio-based interview response"""
    
    # Validate audio file
    validate_audio_file(audio_file)
    
    # Get the question
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question or not question.is_active:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Create response record
    interview_response = InterviewResponse(
        user_id=current_user.id,
        question_id=question_id,
        status="processing"
    )
    
    db.add(interview_response)
    db.commit()
    db.refresh(interview_response)
    
    # Process audio in background
    background_tasks.add_task(
        process_audio_response,
        interview_response.id,
        audio_file,
        question.content,
        question.question_type
    )
    
    # Update question usage
    question_manager = QuestionManager(db)
    question_manager.increment_question_usage(question_id)
    
    # Return initial response
    return ResponseAnalysis(
        response_id=interview_response.id,
        question_id=question.id,
        question_title=question.title,
        status="processing",
        scores={
            "overall_score": 0,
            "content_relevance_score": 0,
            "communication_clarity_score": 0,
            "structure_organization_score": 0,
            "technical_accuracy_score": None,
            "sentiment_score": 0.0,
            "confidence_indicators": 0,
            "filler_words_count": 0,
            "word_count": 0,
            "unique_words_count": 0
        },
        feedback={
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "detailed_feedback": "Processing your audio response...",
            "improvement_tips": "Please wait while we transcribe and analyze your response."
        }
    )


@router.get("/response/{response_id}", response_model=ResponseAnalysis)
async def get_response_analysis(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis results for a specific response"""
    
    # Get the response
    response = db.query(InterviewResponse).filter(
        InterviewResponse.id == response_id,
        InterviewResponse.user_id == current_user.id
    ).first()
    
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # Get the question
    question = db.query(Question).filter(Question.id == response.question_id).first()
    
    # Get the score
    score = db.query(ResponseScore).filter(
        ResponseScore.response_id == response_id
    ).first()
    
    if not score:
        # Response is still processing
        return ResponseAnalysis(
            response_id=response.id,
            question_id=response.question_id,
            question_title=question.title if question else "Unknown",
            original_text=response.original_text,
            processed_text=response.processed_text,
            response_duration_seconds=response.response_duration_seconds,
            transcription_confidence=response.transcription_confidence,
            status=response.status,
            scores={
                "overall_score": 0,
                "content_relevance_score": 0,
                "communication_clarity_score": 0,
                "structure_organization_score": 0,
                "technical_accuracy_score": None,
                "sentiment_score": 0.0,
                "confidence_indicators": 0,
                "filler_words_count": 0,
                "word_count": 0,
                "unique_words_count": 0
            },
            feedback={
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "detailed_feedback": "Still processing...",
                "improvement_tips": "Please wait for analysis to complete."
            }
        )
    
    # Return complete analysis
    return ResponseAnalysis(
        response_id=response.id,
        question_id=response.question_id,
        question_title=question.title if question else "Unknown",
        original_text=response.original_text,
        processed_text=response.processed_text,
        response_duration_seconds=response.response_duration_seconds,
        transcription_confidence=response.transcription_confidence,
        status=response.status,
        processed_at=response.processed_at,
        scoring_model_version=score.scoring_model_version,
        scores={
            "overall_score": score.overall_score,
            "content_relevance_score": score.content_relevance_score,
            "communication_clarity_score": score.communication_clarity_score,
            "structure_organization_score": score.structure_organization_score,
            "technical_accuracy_score": score.technical_accuracy_score,
            "sentiment_score": score.sentiment_score,
            "confidence_indicators": score.confidence_indicators,
            "filler_words_count": score.filler_words_count,
            "word_count": score.word_count,
            "unique_words_count": score.unique_words_count
        },
        feedback={
            "strengths": score.strengths or [],
            "weaknesses": score.weaknesses or [],
            "suggestions": score.suggestions or [],
            "detailed_feedback": score.detailed_feedback,
            "improvement_tips": score.improvement_tips
        }
    )


@router.get("/history", response_model=ResponseHistory)
async def get_response_history(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's response history"""
    
    # Get responses with pagination
    offset = (page - 1) * per_page
    responses = db.query(InterviewResponse).filter(
        InterviewResponse.user_id == current_user.id
    ).order_by(InterviewResponse.created_at.desc()).offset(offset).limit(per_page).all()
    
    total_responses = db.query(InterviewResponse).filter(
        InterviewResponse.user_id == current_user.id
    ).count()
    
    # Convert to response analysis format
    response_analyses = []
    total_score = 0
    completed_responses = 0
    
    for response in responses:
        question = db.query(Question).filter(Question.id == response.question_id).first()
        score = db.query(ResponseScore).filter(ResponseScore.response_id == response.id).first()
        
        if score:
            total_score += score.overall_score
            completed_responses += 1
            
            analysis = ResponseAnalysis(
                response_id=response.id,
                question_id=response.question_id,
                question_title=question.title if question else "Unknown",
                original_text=response.original_text,
                processed_text=response.processed_text,
                response_duration_seconds=response.response_duration_seconds,
                transcription_confidence=response.transcription_confidence,
                status=response.status,
                processed_at=response.processed_at,
                scoring_model_version=score.scoring_model_version,
                scores={
                    "overall_score": score.overall_score,
                    "content_relevance_score": score.content_relevance_score,
                    "communication_clarity_score": score.communication_clarity_score,
                    "structure_organization_score": score.structure_organization_score,
                    "technical_accuracy_score": score.technical_accuracy_score,
                    "sentiment_score": score.sentiment_score,
                    "confidence_indicators": score.confidence_indicators,
                    "filler_words_count": score.filler_words_count,
                    "word_count": score.word_count,
                    "unique_words_count": score.unique_words_count
                },
                feedback={
                    "strengths": score.strengths or [],
                    "weaknesses": score.weaknesses or [],
                    "suggestions": score.suggestions or [],
                    "detailed_feedback": score.detailed_feedback,
                    "improvement_tips": score.improvement_tips
                }
            )
        else:
            # Response still processing
            analysis = ResponseAnalysis(
                response_id=response.id,
                question_id=response.question_id,
                question_title=question.title if question else "Unknown",
                original_text=response.original_text,
                processed_text=response.processed_text,
                status=response.status,
                scores={
                    "overall_score": 0,
                    "content_relevance_score": 0,
                    "communication_clarity_score": 0,
                    "structure_organization_score": 0,
                    "technical_accuracy_score": None,
                    "sentiment_score": 0.0,
                    "confidence_indicators": 0,
                    "filler_words_count": 0,
                    "word_count": 0,
                    "unique_words_count": 0
                },
                feedback={
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": [],
                    "detailed_feedback": "Processing...",
                    "improvement_tips": "Analysis in progress."
                }
            )
        
        response_analyses.append(analysis)
    
    # Calculate average score
    average_score = total_score / completed_responses if completed_responses > 0 else None
    
    return ResponseHistory(
        responses=response_analyses,
        total_responses=total_responses,
        average_overall_score=average_score,
        improvement_trend="stable"  # Could be calculated based on recent scores
    )


# Background task functions

async def process_text_response(response_id: int, text: str, question: str, question_type: str):
    """Background task to process text response"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        start_time = time.time()
        
        # Get the response record
        response = db.query(InterviewResponse).filter(InterviewResponse.id == response_id).first()
        if not response:
            return
        
        # Initialize NLP scorer
        nlp_scorer = NLPScorer()
        
        # Score the response
        scoring_result = await nlp_scorer.score_response(text, question, question_type)
        
        # Create score record
        score = ResponseScore(
            response_id=response_id,
            overall_score=scoring_result['scores']['overall_score'],
            content_relevance_score=scoring_result['scores']['content_relevance_score'],
            communication_clarity_score=scoring_result['scores']['communication_clarity_score'],
            structure_organization_score=scoring_result['scores']['structure_organization_score'],
            technical_accuracy_score=scoring_result['scores'].get('technical_accuracy_score'),
            sentiment_score=scoring_result['scores']['sentiment_score'],
            confidence_indicators=scoring_result['scores']['confidence_indicators'],
            filler_words_count=scoring_result['scores']['filler_words_count'],
            word_count=scoring_result['scores']['word_count'],
            unique_words_count=scoring_result['scores']['unique_words_count'],
            strengths=scoring_result['feedback'].get('strengths', []),
            weaknesses=scoring_result['feedback'].get('weaknesses', []),
            suggestions=scoring_result['feedback'].get('suggestions', []),
            detailed_feedback=scoring_result['feedback']['detailed_feedback'],
            improvement_tips=scoring_result['feedback']['improvement_tips'],
            scoring_model_version="nlp_v1.0"
        )
        
        db.add(score)
        
        # Update response status
        response.status = "completed"
        response.processed_at = time.time()
        response.processing_time_ms = int((time.time() - start_time) * 1000)
        
        db.commit()
        
        # Update question average score
        question_manager = QuestionManager(db)
        question_manager.update_question_average_score(
            response.question_id, 
            scoring_result['scores']['overall_score']
        )
        
    except Exception as e:
        # Update response with error
        response = db.query(InterviewResponse).filter(InterviewResponse.id == response_id).first()
        if response:
            response.status = "failed"
            response.error_message = str(e)
            db.commit()
        
        print(f"Error processing text response {response_id}: {e}")
    
    finally:
        db.close()


async def process_audio_response(response_id: int, audio_file: UploadFile, question: str, question_type: str):
    """Background task to process audio response"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        start_time = time.time()
        
        # Get the response record
        response = db.query(InterviewResponse).filter(InterviewResponse.id == response_id).first()
        if not response:
            return
        
        # Initialize audio processor
        audio_processor = AudioProcessor()
        
        # Process audio file
        transcribed_text, confidence, duration = await audio_processor.process_audio_file(audio_file)
        
        # Save audio file
        audio_path = await audio_processor.save_audio_file(audio_file, response.user_id, response_id)
        
        # Clean transcribed text
        cleaned_text = clean_text_input(transcribed_text)
        
        # Update response with transcription results
        response.original_text = transcribed_text
        response.processed_text = cleaned_text
        response.audio_file_path = audio_path
        response.response_duration_seconds = duration
        response.transcription_confidence = confidence
        
        # Score the response
        nlp_scorer = NLPScorer()
        scoring_result = await nlp_scorer.score_response(cleaned_text, question, question_type)
        
        # Create score record
        score = ResponseScore(
            response_id=response_id,
            overall_score=scoring_result['scores']['overall_score'],
            content_relevance_score=scoring_result['scores']['content_relevance_score'],
            communication_clarity_score=scoring_result['scores']['communication_clarity_score'],
            structure_organization_score=scoring_result['scores']['structure_organization_score'],
            technical_accuracy_score=scoring_result['scores'].get('technical_accuracy_score'),
            sentiment_score=scoring_result['scores']['sentiment_score'],
            confidence_indicators=scoring_result['scores']['confidence_indicators'],
            filler_words_count=scoring_result['scores']['filler_words_count'],
            word_count=scoring_result['scores']['word_count'],
            unique_words_count=scoring_result['scores']['unique_words_count'],
            strengths=scoring_result['feedback'].get('strengths', []),
            weaknesses=scoring_result['feedback'].get('weaknesses', []),
            suggestions=scoring_result['feedback'].get('suggestions', []),
            detailed_feedback=scoring_result['feedback']['detailed_feedback'],
            improvement_tips=scoring_result['feedback']['improvement_tips'],
            scoring_model_version="nlp_v1.0"
        )
        
        db.add(score)
        
        # Update response status
        response.status = "completed"
        response.processed_at = time.time()
        response.processing_time_ms = int((time.time() - start_time) * 1000)
        
        db.commit()
        
        # Update question average score
        question_manager = QuestionManager(db)
        question_manager.update_question_average_score(
            response.question_id, 
            scoring_result['scores']['overall_score']
        )
        
    except Exception as e:
        # Update response with error
        response = db.query(InterviewResponse).filter(InterviewResponse.id == response_id).first()
        if response:
            response.status = "failed"
            response.error_message = str(e)
            db.commit()
        
        print(f"Error processing audio response {response_id}: {e}")
    
    finally:
        db.close()
