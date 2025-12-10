from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.tutor import TutorRequest, TutorResponse, MCQGenerationRequest, VoiceGenerationRequest, VoiceGenerationResponse
from app.services.ai_service import AIService
from app.services.rag_service import RAGService
from app.services.voice_service import VoiceService
from app.api.dependencies import get_current_user
from app.models import User
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(
    request: TutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ask the tutor a question - uses RAG to provide curriculum-based answers
    
    Process:
    1. Query ChromaDB for relevant curriculum chunks
    2. Pass chunks as context to AI model
    3. Model generates answer based ONLY on curriculum context
    4. Return response with sources
    
    - **query**: Your question (5-2000 characters)
    - **subject**: Subject area (optional but recommended)
    - **topic**: Specific topic (optional)
    - **language**: Response language (en, yo, ha, ig)
    """
    try:
        logger.info(f"Tutor query from user {current_user.id}: {request.query[:50]}")
        
        # Query RAG for relevant curriculum chunks
        rag = RAGService()
        rag_results = rag.search_syllabus(
            query=request.query,
            subject=request.subject,
            top_k=5  # Get top 5 most relevant chunks
        )
        
        if not rag_results:
            logger.warning(f"No curriculum found for: {request.query}")
            return TutorResponse(
                response_text="I don't have curriculum information about this topic. Please upload the relevant curriculum PDF first.",
                response_audio_url=None,
                language=request.language,
                sources=None,
            )
        
        # Build context from RAG results
        context = "\n\n".join([
            f"[{result['metadata'].get('subject', '')}] {result['content']}"
            for result in rag_results
        ])
        
        logger.info(f"Found {len(rag_results)} relevant curriculum chunks")
        
        # Generate response using RAG context
        response_text = await AIService.generate_text(
            query=request.query,
            language=request.language,
            context=context,  # Pass curriculum context
            max_tokens=512,
            temperature=0.5,  # Lower temperature for factual answers
            system_role="tutor"
        )
        
        return TutorResponse(
            response_text=response_text,
            response_audio_url=None,  # Voice generation to be implemented
            language=request.language,
            sources=[{
                "subject": result["metadata"].get("subject"),
                "source": result["metadata"].get("source"),
                "chunk_index": result["metadata"].get("chunk_index"),
            } for result in rag_results[:3]],
        )
        
    except Exception as e:
        logger.error(f"Tutor query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response",
        )


@router.post("/generate-mcq", response_model=dict)
async def generate_mcq(
    request: MCQGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate multiple-choice questions for a subject and topic
    
    - **subject**: Subject name
    - **topic**: Topic name
    - **number_of_questions**: Number of questions (1-20)
    - **difficulty**: easy, medium, or hard
    - **language**: en, yo, ha, or ig
    """
    try:
        logger.info(f"MCQ generation from user {current_user.id}: {request.subject} - {request.topic}")
        
        # Generate MCQs
        mcq_response = await AIService.generate_mcq(
            subject=request.subject,
            topic=request.topic,
            number_of_questions=request.number_of_questions,
            difficulty=request.difficulty or "medium",
            language=request.language,
        )
        
        return {
            "questions": mcq_response,
            "subject": request.subject,
            "topic": request.topic,
            "language": request.language,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error(f"MCQ generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate MCQs",
        )


@router.post("/generate-voice", response_model=VoiceGenerationResponse)
async def generate_voice(
    request: VoiceGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate voice/audio from text using text-to-speech
    
    - **text**: Text to convert to speech (5-5000 characters)
    - **language**: Language code (en, yo, ha, ig)
    """
    try:
        logger.info(f"Voice generation from user {current_user.id}")
        
        # Generate voice
        audio_url = await VoiceService.generate_speech(
            text=request.text,
            language=request.language,
        )
        
        return VoiceGenerationResponse(
            audio_url=audio_url,
            language=request.language,
            duration_seconds=len(request.text) / 100,  # Rough estimate
        )
        
    except Exception as e:
        logger.error(f"Voice generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate voice",
        )


@router.post("/process-voice-query")
async def process_voice_query(
    file: UploadFile = File(...),
    subject: str = None,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Process voice/audio input and return text + voice response
    
    Process:
    1. Convert audio to text (speech-to-text)
    2. Process as normal tutor query
    3. Return response as text + voice
    
    - **file**: Audio file (MP3, WAV, OGG)
    - **subject**: Subject area (optional)
    - **language**: Language code (en, yo, ha, ig)
    """
    try:
        if not file.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only audio files (MP3, WAV, OGG, M4A) are supported",
            )
        
        logger.info(f"Voice query from user {current_user.id}")
        
        # Convert audio to text
        audio_content = await file.read()
        query_text = await VoiceService.transcribe_audio(
            audio_data=audio_content,
            language=language,
        )
        
        logger.info(f"Transcribed query: {query_text[:50]}")
        
        # Process as normal tutor query
        rag = RAGService()
        rag_results = rag.search_syllabus(
            query=query_text,
            subject=subject,
            top_k=5
        )
        
        if not rag_results:
            response_text = "I don't have curriculum information about this topic."
            sources = None
        else:
            context = "\n\n".join([
                f"[{result['metadata'].get('subject', '')}] {result['content']}"
                for result in rag_results
            ])
            
            response_text = await AIService.generate_text(
                query=query_text,
                language=language,
                context=context,
                max_tokens=512,
                temperature=0.5,
                system_role="tutor"
            )
            
            sources = [{
                "subject": result["metadata"].get("subject"),
                "source": result["metadata"].get("source"),
            } for result in rag_results[:3]]
        
        # Generate voice response
        response_audio_url = await VoiceService.generate_speech(
            text=response_text,
            language=language,
        )
        
        return {
            "transcribed_query": query_text,
            "response_text": response_text,
            "response_audio_url": response_audio_url,
            "language": language,
            "sources": sources,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice query processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice query",
        )