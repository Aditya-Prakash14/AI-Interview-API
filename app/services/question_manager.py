"""
Question management service for admin operations
"""
import json
import csv
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, UploadFile

from app.models.question import Question, QuestionCategory
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionFilters
from app.utils.validators import validate_text_input


class QuestionManager:
    """Service for managing interview questions and categories"""
    
    def __init__(self, db: Session):
        """Initialize the question manager with database session"""
        self.db = db
    
    def create_question(self, question_data: QuestionCreate, creator_id: int) -> Question:
        """Create a new interview question"""
        # Validate input data
        validate_text_input(question_data.content, min_length=20, max_length=2000)
        validate_text_input(question_data.title, min_length=10, max_length=255)
        
        # Create question object
        question = Question(
            title=question_data.title,
            content=question_data.content,
            difficulty_level=question_data.difficulty_level,
            question_type=question_data.question_type,
            expected_duration_minutes=question_data.expected_duration_minutes,
            scoring_criteria=question_data.scoring_criteria,
            sample_answer=question_data.sample_answer,
            keywords=question_data.keywords,
            created_by=creator_id
        )
        
        # Add categories if specified
        if question_data.category_ids:
            categories = self.db.query(QuestionCategory).filter(
                QuestionCategory.id.in_(question_data.category_ids)
            ).all()
            question.categories = categories
        
        # Save to database
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def update_question(self, question_id: int, question_data: QuestionUpdate) -> Question:
        """Update an existing question"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update fields if provided
        update_data = question_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "category_ids":
                if value is not None:
                    categories = self.db.query(QuestionCategory).filter(
                        QuestionCategory.id.in_(value)
                    ).all()
                    question.categories = categories
            else:
                setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def delete_question(self, question_id: int) -> bool:
        """Soft delete a question by setting is_active to False"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question.is_active = False
        self.db.commit()
        
        return True
    
    def get_question(self, question_id: int) -> Optional[Question]:
        """Get a single question by ID"""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def get_questions(self, filters: QuestionFilters, page: int = 1, 
                     per_page: int = 20) -> Tuple[List[Question], int]:
        """Get questions with filtering and pagination"""
        query = self.db.query(Question)
        
        # Apply filters
        if filters.category_id:
            query = query.join(Question.categories).filter(
                QuestionCategory.id == filters.category_id
            )
        
        if filters.difficulty_level:
            query = query.filter(Question.difficulty_level == filters.difficulty_level)
        
        if filters.question_type:
            query = query.filter(Question.question_type == filters.question_type)
        
        if filters.is_active is not None:
            query = query.filter(Question.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Question.title.ilike(search_term),
                    Question.content.ilike(search_term),
                    Question.keywords.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        questions = query.offset(offset).limit(per_page).all()
        
        return questions, total
    
    def get_random_questions(self, count: int = 5, difficulty_level: Optional[str] = None,
                           question_type: Optional[str] = None) -> List[Question]:
        """Get random questions for interview sessions"""
        query = self.db.query(Question).filter(Question.is_active == True)
        
        if difficulty_level:
            query = query.filter(Question.difficulty_level == difficulty_level)
        
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        # Get random questions
        questions = query.order_by(func.random()).limit(count).all()
        
        return questions
    
    def create_category(self, name: str, description: Optional[str] = None, 
                       color: str = "#007bff") -> QuestionCategory:
        """Create a new question category"""
        # Check if category already exists
        existing = self.db.query(QuestionCategory).filter(
            QuestionCategory.name == name
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        category = QuestionCategory(
            name=name,
            description=description,
            color=color
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def update_category(self, category_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, 
                       color: Optional[str] = None,
                       is_active: Optional[bool] = None) -> QuestionCategory:
        """Update a question category"""
        category = self.db.query(QuestionCategory).filter(
            QuestionCategory.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if name is not None:
            # Check for duplicate names
            existing = self.db.query(QuestionCategory).filter(
                and_(QuestionCategory.name == name, QuestionCategory.id != category_id)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Category name already exists")
            category.name = name
        
        if description is not None:
            category.description = description
        
        if color is not None:
            category.color = color
        
        if is_active is not None:
            category.is_active = is_active
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category (soft delete)"""
        category = self.db.query(QuestionCategory).filter(
            QuestionCategory.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category.is_active = False
        self.db.commit()
        
        return True
    
    def get_categories(self, active_only: bool = True) -> List[QuestionCategory]:
        """Get all question categories"""
        query = self.db.query(QuestionCategory)
        
        if active_only:
            query = query.filter(QuestionCategory.is_active == True)
        
        return query.all()
    
    def bulk_import_questions(self, file: UploadFile, creator_id: int) -> Dict:
        """Import questions from CSV file"""
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        try:
            # Read CSV content
            content = file.file.read().decode('utf-8')
            csv_reader = csv.DictReader(content.splitlines())
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    required_fields = ['title', 'content', 'difficulty_level', 'question_type']
                    for field in required_fields:
                        if not row.get(field):
                            raise ValueError(f"Missing required field: {field}")
                    
                    # Create question
                    question_data = QuestionCreate(
                        title=row['title'].strip(),
                        content=row['content'].strip(),
                        difficulty_level=row['difficulty_level'].strip().lower(),
                        question_type=row['question_type'].strip().lower(),
                        expected_duration_minutes=int(row.get('expected_duration_minutes', 5)),
                        scoring_criteria=row.get('scoring_criteria', '').strip() or None,
                        sample_answer=row.get('sample_answer', '').strip() or None,
                        keywords=row.get('keywords', '').strip() or None,
                        category_ids=[]
                    )
                    
                    # Handle categories
                    if row.get('categories'):
                        category_names = [name.strip() for name in row['categories'].split(',')]
                        category_ids = []
                        
                        for cat_name in category_names:
                            category = self.db.query(QuestionCategory).filter(
                                QuestionCategory.name == cat_name
                            ).first()
                            
                            if not category:
                                # Create category if it doesn't exist
                                category = self.create_category(cat_name)
                            
                            category_ids.append(category.id)
                        
                        question_data.category_ids = category_ids
                    
                    # Create the question
                    self.create_question(question_data, creator_id)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return {
                'imported_count': imported_count,
                'errors': errors,
                'total_rows': row_num - 1 if 'row_num' in locals() else 0
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")
    
    def export_questions(self, filters: Optional[QuestionFilters] = None) -> str:
        """Export questions to CSV format"""
        if not filters:
            filters = QuestionFilters()
        
        questions, _ = self.get_questions(filters, page=1, per_page=10000)
        
        # Create CSV content
        csv_lines = []
        headers = [
            'id', 'title', 'content', 'difficulty_level', 'question_type',
            'expected_duration_minutes', 'scoring_criteria', 'sample_answer',
            'keywords', 'categories', 'usage_count', 'average_score',
            'is_active', 'created_at'
        ]
        csv_lines.append(','.join(headers))
        
        for question in questions:
            categories = ','.join([cat.name for cat in question.categories])
            
            row = [
                str(question.id),
                f'"{question.title}"',
                f'"{question.content}"',
                question.difficulty_level,
                question.question_type,
                str(question.expected_duration_minutes),
                f'"{question.scoring_criteria or ""}"',
                f'"{question.sample_answer or ""}"',
                f'"{question.keywords or ""}"',
                f'"{categories}"',
                str(question.usage_count),
                str(question.average_score or ""),
                str(question.is_active),
                question.created_at.isoformat()
            ]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def get_question_statistics(self) -> Dict:
        """Get statistics about questions in the database"""
        total_questions = self.db.query(Question).count()
        active_questions = self.db.query(Question).filter(Question.is_active == True).count()
        
        # Questions by difficulty
        difficulty_stats = self.db.query(
            Question.difficulty_level,
            func.count(Question.id).label('count')
        ).filter(Question.is_active == True).group_by(Question.difficulty_level).all()
        
        # Questions by type
        type_stats = self.db.query(
            Question.question_type,
            func.count(Question.id).label('count')
        ).filter(Question.is_active == True).group_by(Question.question_type).all()
        
        # Most used questions
        popular_questions = self.db.query(Question).filter(
            Question.is_active == True
        ).order_by(Question.usage_count.desc()).limit(5).all()
        
        return {
            'total_questions': total_questions,
            'active_questions': active_questions,
            'inactive_questions': total_questions - active_questions,
            'difficulty_distribution': {stat.difficulty_level: stat.count for stat in difficulty_stats},
            'type_distribution': {stat.question_type: stat.count for stat in type_stats},
            'popular_questions': [
                {'id': q.id, 'title': q.title, 'usage_count': q.usage_count}
                for q in popular_questions
            ],
            'total_categories': self.db.query(QuestionCategory).filter(
                QuestionCategory.is_active == True
            ).count()
        }
    
    def increment_question_usage(self, question_id: int):
        """Increment the usage count for a question"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if question:
            question.usage_count += 1
            self.db.commit()
    
    def update_question_average_score(self, question_id: int, new_score: int):
        """Update the average score for a question"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if question:
            if question.average_score is None:
                question.average_score = new_score
            else:
                # Simple moving average (could be improved with proper calculation)
                question.average_score = int((question.average_score + new_score) / 2)
            self.db.commit()
