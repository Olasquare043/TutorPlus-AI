from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.mcq import (
    MCQResponse, MCQCreate, MCQAttemptCreate, MCQAttemptResponse
)
from app.models import MCQ, MCQOption, MCQAttempt
from app.api.dependencies import get_current_user
from app.models import User
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcq", tags=["mcq"])


@router.get("/{mcq_id}", response_model=MCQResponse)
async def get_mcq(
    mcq_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific MCQ question with options"""
    try:
        mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()
        
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ not found",
            )
        
        return mcq
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch MCQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch MCQ",
        )


@router.get("/subject/{subject}", response_model=list[MCQResponse])
async def get_mcq_by_subject(
    subject: str,
    topic: str = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get MCQs by subject and optional topic"""
    try:
        query = db.query(MCQ).filter(
            (MCQ.subject == subject) &
            (MCQ.is_active == True)
        )
        
        if topic:
            query = query.filter(MCQ.topic == topic)
        
        mcqs = query.limit(limit).all()
        
        return mcqs
        
    except Exception as e:
        logger.error(f"Failed to fetch MCQs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch MCQs",
        )


@router.post("/attempt", response_model=MCQAttemptResponse)
async def submit_mcq_attempt(
    attempt: MCQAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an MCQ attempt and get grading"""
    try:
        logger.info(f"MCQ attempt from user {current_user.id}")
        
        # Get MCQ
        mcq = db.query(MCQ).filter(MCQ.id == attempt.mcq_id).first()
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ not found",
            )
        
        # Check if selected option is correct
        is_correct = False
        if attempt.selected_option_id:
            option = db.query(MCQOption).filter(
                MCQOption.id == attempt.selected_option_id
            ).first()
            is_correct = option.is_correct if option else False
        
        # Record attempt
        mcq_attempt = MCQAttempt(
            user_id=current_user.id,
            mcq_id=attempt.mcq_id,
            selected_option_id=attempt.selected_option_id,
            is_correct=is_correct,
            time_spent_seconds=attempt.time_spent_seconds,
        )
        
        db.add(mcq_attempt)
        db.commit()
        db.refresh(mcq_attempt)
        
        logger.info(f"MCQ attempt recorded: {mcq_attempt.id}")
        return mcq_attempt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit MCQ attempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit attempt",
        )


@router.get("/attempts/my", response_model=list[MCQAttemptResponse])
async def get_user_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all MCQ attempts by current user"""
    try:
        attempts = db.query(MCQAttempt).filter(
            MCQAttempt.user_id == current_user.id
        ).all()
        
        return attempts
        
    except Exception as e:
        logger.error(f"Failed to fetch attempts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attempts",
        )