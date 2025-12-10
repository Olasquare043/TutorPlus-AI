from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user
from app.models import User
from app.services.rag_pipeline import RAGPipeline
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/upload-curriculum")
async def upload_curriculum_pdf(
    file: UploadFile = File(...),
    subject: str = None,
    grade_level: str = None,
    exam_board: str = "WAEC",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload and process a curriculum PDF
    
    The PDF will be:
    1. Extracted (text from pages)
    2. Cleaned (remove noise)
    3. Chunked (split into manageable pieces with metadata)
    4. Embedded (converted to vectors)
    5. Stored in ChromaDB (for RAG queries)
    
    Args:
        file: PDF file to upload
        subject: Subject name (e.g., "Biology")
        grade_level: Grade level (e.g., "SSS3")
        exam_board: Exam board (WAEC, NECO, JAMB)
    """
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )
        
        if not subject or not grade_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="subject and grade_level are required",
            )
        
        logger.info(f"User {current_user.id} uploading curriculum: {file.filename}")
        
        # Process PDF through RAG pipeline
        result = await RAGPipeline.process_curriculum_pdf(
            pdf_file=file,
            subject=subject,
            grade_level=grade_level,
            exam_board=exam_board,
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed {result['chunks_created']} chunks from {file.filename}",
            "data": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Curriculum upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process curriculum: {str(e)}",
        )


@router.get("/curriculum-stats")
async def get_curriculum_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get statistics about loaded curriculum data in ChromaDB
    """
    try:
        from app.services.rag_service import RAGService
        
        rag = RAGService()
        collection = rag.get_collection()
        
        # Get collection count
        count = collection.count()
        
        return {
            "status": "success",
            "total_chunks": count,
            "message": f"ChromaDB contains {count} chunks",
        }
        
    except Exception as e:
        logger.error(f"Failed to get curriculum stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics",
        )