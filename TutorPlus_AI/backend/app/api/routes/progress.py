from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.progress import (
    ProgressResponse, ProgressCreate, ProgressUpdate,
    StudentProgressResponse, StudentProgressUpdate
)
from app.models import Progress, StudentProgress
from app.api.dependencies import get_current_user
from app.models import User
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/my", response_model=list[ProgressResponse])
async def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's learning progress across all subjects"""
    try:
        progress_items = db.query(Progress).filter(
            Progress.user_id == current_user.id
        ).all()
        
        return progress_items
        
    except Exception as e:
        logger.error(f"Failed to fetch progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch progress",
        )


@router.post("/track", response_model=ProgressResponse)
async def track_progress(
    progress_create: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Track learning progress for a subject and topic"""
    try:
        logger.info(f"Tracking progress for user {current_user.id}: {progress_create.subject}")
        
        # Check if progress record exists
        existing_progress = db.query(Progress).filter(
            (Progress.user_id == current_user.id) &
            (Progress.subject == progress_create.subject) &
            (Progress.topic == progress_create.topic)
        ).first()
        
        if existing_progress:
            # Update existing
            for field, value in progress_create.model_dump().items():
                setattr(existing_progress, field, value)
            db.commit()
            db.refresh(existing_progress)
            return existing_progress
        
        # Create new
        progress = Progress(
            user_id=current_user.id,
            subject=progress_create.subject,
            topic=progress_create.topic,
            lessons_completed=progress_create.lessons_completed,
            total_lessons=progress_create.total_lessons,
            quiz_score=progress_create.quiz_score,
        )
        
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        logger.info(f"Progress tracked successfully")
        return progress
        
    except Exception as e:
        logger.error(f"Failed to track progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track progress",
        )


@router.get("/student/{subject}", response_model=StudentProgressResponse)
async def get_student_progress(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get student progress for a specific subject"""
    try:
        student_progress = db.query(StudentProgress).filter(
            (StudentProgress.user_id == current_user.id) &
            (StudentProgress.subject == subject)
        ).first()
        
        if not student_progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress not found for this subject",
            )
        
        return student_progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch student progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch progress",
        )


@router.put("/student/{subject}", response_model=StudentProgressResponse)
async def update_student_progress(
    subject: str,
    progress_update: StudentProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update student progress for a subject"""
    try:
        student_progress = db.query(StudentProgress).filter(
            (StudentProgress.user_id == current_user.id) &
            (StudentProgress.subject == subject)
        ).first()
        
        if not student_progress:
            # Create new if doesn't exist
            student_progress = StudentProgress(
                user_id=current_user.id,
                subject=subject,
            )
            db.add(student_progress)
        
        # Update fields
        update_data = progress_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student_progress, field, value)
        
        db.commit()
        db.refresh(student_progress)
        
        logger.info(f"Student progress updated for subject: {subject}")
        return student_progress
        
    except Exception as e:
        logger.error(f"Failed to update student progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update progress",
        )