"""
Admin API routes for question management and analytics
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionCreate, QuestionResponse, QuestionUpdate, QuestionListResponse,
    CategoryCreate, CategoryResponse, CategoryUpdate, QuestionFilters
)
from app.utils.security import get_current_admin_user
from app.services.question_manager import QuestionManager

router = APIRouter(prefix="/admin", tags=["admin"])


# Question Management

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new interview question"""
    
    question_manager = QuestionManager(db)
    question = question_manager.create_question(question_data, current_admin.id)
    
    return question


@router.get("/questions", response_model=QuestionListResponse)
async def get_questions(
    page: int = 1,
    per_page: int = 20,
    category_id: Optional[int] = None,
    difficulty_level: Optional[str] = None,
    question_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get questions with filtering and pagination"""
    
    filters = QuestionFilters(
        category_id=category_id,
        difficulty_level=difficulty_level,
        question_type=question_type,
        is_active=is_active,
        search=search
    )
    
    question_manager = QuestionManager(db)
    questions, total = question_manager.get_questions(filters, page, per_page)
    
    total_pages = (total + per_page - 1) // per_page
    
    return QuestionListResponse(
        questions=questions,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific question by ID"""
    
    question_manager = QuestionManager(db)
    question = question_manager.get_question(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update an existing question"""
    
    question_manager = QuestionManager(db)
    question = question_manager.update_question(question_id, question_data)
    
    return question


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a question (soft delete)"""
    
    question_manager = QuestionManager(db)
    success = question_manager.delete_question(question_id)
    
    if success:
        return {"message": "Question deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Question not found")


@router.post("/questions/bulk-import")
async def bulk_import_questions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Bulk import questions from CSV file"""
    
    question_manager = QuestionManager(db)
    result = question_manager.bulk_import_questions(file, current_admin.id)
    
    return {
        "message": f"Import completed. {result['imported_count']} questions imported.",
        "imported_count": result['imported_count'],
        "total_rows": result['total_rows'],
        "errors": result['errors']
    }


@router.get("/questions/export")
async def export_questions(
    category_id: Optional[int] = None,
    difficulty_level: Optional[str] = None,
    question_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Export questions to CSV"""
    
    filters = QuestionFilters(
        category_id=category_id,
        difficulty_level=difficulty_level,
        question_type=question_type,
        is_active=is_active,
        search=search
    )
    
    question_manager = QuestionManager(db)
    csv_content = question_manager.export_questions(filters)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questions_export.csv"}
    )


# Category Management

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new question category"""
    
    question_manager = QuestionManager(db)
    category = question_manager.create_category(
        name=category_data.name,
        description=category_data.description,
        color=category_data.color
    )
    
    return category


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all question categories"""
    
    question_manager = QuestionManager(db)
    categories = question_manager.get_categories(active_only)
    
    return categories


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a question category"""
    
    question_manager = QuestionManager(db)
    category = question_manager.update_category(
        category_id=category_id,
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        is_active=category_data.is_active
    )
    
    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a category (soft delete)"""
    
    question_manager = QuestionManager(db)
    success = question_manager.delete_category(category_id)
    
    if success:
        return {"message": "Category deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Category not found")


# Analytics and Statistics

@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get comprehensive statistics about the system"""
    
    question_manager = QuestionManager(db)
    question_stats = question_manager.get_question_statistics()
    
    # Get user statistics
    from app.models.user import User
    from app.models.response import InterviewResponse, ResponseScore
    from sqlalchemy import func
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    total_responses = db.query(InterviewResponse).count()
    completed_responses = db.query(InterviewResponse).filter(
        InterviewResponse.status == "completed"
    ).count()
    
    # Average scores
    avg_score_result = db.query(func.avg(ResponseScore.overall_score)).scalar()
    average_score = round(avg_score_result, 2) if avg_score_result else 0
    
    # Recent activity (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_responses = db.query(InterviewResponse).filter(
        InterviewResponse.created_at >= week_ago
    ).count()
    
    recent_users = db.query(User).filter(
        User.created_at >= week_ago
    ).count()
    
    return {
        "questions": question_stats,
        "users": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "new_users_this_week": recent_users
        },
        "responses": {
            "total_responses": total_responses,
            "completed_responses": completed_responses,
            "pending_responses": total_responses - completed_responses,
            "responses_this_week": recent_responses,
            "average_score": average_score
        },
        "system": {
            "database_status": "healthy",
            "last_updated": datetime.utcnow().isoformat()
        }
    }


@router.get("/analytics/performance")
async def get_performance_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get performance analytics over time"""
    
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily response counts
    daily_responses = db.query(
        func.date(InterviewResponse.created_at).label('date'),
        func.count(InterviewResponse.id).label('count')
    ).filter(
        InterviewResponse.created_at >= start_date
    ).group_by(func.date(InterviewResponse.created_at)).all()
    
    # Daily average scores
    daily_scores = db.query(
        func.date(InterviewResponse.created_at).label('date'),
        func.avg(ResponseScore.overall_score).label('avg_score')
    ).join(ResponseScore).filter(
        InterviewResponse.created_at >= start_date
    ).group_by(func.date(InterviewResponse.created_at)).all()
    
    # Question type performance
    type_performance = db.query(
        Question.question_type,
        func.avg(ResponseScore.overall_score).label('avg_score'),
        func.count(ResponseScore.id).label('response_count')
    ).join(InterviewResponse).join(ResponseScore).filter(
        InterviewResponse.created_at >= start_date
    ).group_by(Question.question_type).all()
    
    # Difficulty level performance
    difficulty_performance = db.query(
        Question.difficulty_level,
        func.avg(ResponseScore.overall_score).label('avg_score'),
        func.count(ResponseScore.id).label('response_count')
    ).join(InterviewResponse).join(ResponseScore).filter(
        InterviewResponse.created_at >= start_date
    ).group_by(Question.difficulty_level).all()
    
    return {
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "daily_responses": [
            {"date": str(item.date), "count": item.count}
            for item in daily_responses
        ],
        "daily_average_scores": [
            {"date": str(item.date), "avg_score": round(item.avg_score, 2)}
            for item in daily_scores if item.avg_score
        ],
        "question_type_performance": [
            {
                "question_type": item.question_type,
                "avg_score": round(item.avg_score, 2),
                "response_count": item.response_count
            }
            for item in type_performance
        ],
        "difficulty_performance": [
            {
                "difficulty_level": item.difficulty_level,
                "avg_score": round(item.avg_score, 2),
                "response_count": item.response_count
            }
            for item in difficulty_performance
        ]
    }


@router.get("/users")
async def get_users(
    page: int = 1,
    per_page: int = 20,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get list of users with pagination"""
    
    query = db.query(User)
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    total = query.count()
    offset = (page - 1) * per_page
    users = query.offset(offset).limit(per_page).all()
    
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Toggle user active status"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }
