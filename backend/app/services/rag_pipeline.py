import logging
from typing import List, Dict, Optional
import os
from pathlib import Path
import tempfile
import uuid
from datetime import datetime,UTC

import pypdf
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for PDF curriculum processing"""
    
    # Chunking parameters
    CHUNK_SIZE = 1000  # characters per chunk
    CHUNK_OVERLAP = 200  # overlap between chunks
    
    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            text = ""
            with open(pdf_path, "rb") as pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                num_pages = len(reader.pages)
                
                logger.info(f"PDF has {num_pages} pages")
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        try:
            logger.info("Cleaning text...")
            
            # Remove extra whitespace
            text = " ".join(text.split())
            
            # Remove special characters (keep some)
            text = text.replace("\x00", "")
            
            # Fix common OCR errors
            text = text.replace("I ", "1 ")
            
            logger.info(f"Cleaned text: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}")
            raise
    
    @staticmethod
    def chunk_text(text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Base metadata for chunks
            
        Returns:
            List of chunks with metadata
        """
        try:
            logger.info("Chunking text...")
            
            # Split text
            chunks = RAGPipeline.text_splitter.split_text(text)
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Add metadata to each chunk
            chunked_data = []
            for idx, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = idx
                chunk_metadata["chunk_count"] = len(chunks)
                chunk_metadata["timestamp"] = datetime.now(UTC).isoformat()
                
                chunked_data.append({
                    "id": str(uuid.uuid4()),
                    "content": chunk,
                    "metadata": chunk_metadata,
                })
            
            logger.info(f"Added metadata to {len(chunked_data)} chunks")
            return chunked_data
            
        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}")
            raise
    
    @staticmethod
    async def process_curriculum_pdf(
        pdf_file,
        subject: str,
        grade_level: str,
        exam_board: str = "WAEC",
        ) -> Dict:
        """
        Complete pipeline: PDF → Extract → Clean → Chunk → Embed → Store
        
        Args:
            pdf_file: Uploaded PDF file object
            subject: Subject name (e.g., "Biology")
            grade_level: Grade level (e.g., "SSS3")
            exam_board: Exam board (WAEC, NECO, JAMB)
            
        Returns:
            Summary of processing
        """
        try:
            logger.info(f"Starting RAG pipeline for {subject} ({grade_level})")
            
            # Step 1: Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_content = await pdf_file.read()
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name
            
            # Step 2: Extract text from PDF
            raw_text = RAGPipeline.extract_text_from_pdf(tmp_path)
            
            # Step 3: Clean text
            cleaned_text = RAGPipeline.clean_text(raw_text)
            
            # Step 4: Chunk with metadata
            base_metadata = {
                "subject": subject,
                "grade_level": grade_level,
                "exam_board": exam_board,
                "source": pdf_file.filename,
            }
            
            chunks = RAGPipeline.chunk_text(cleaned_text, base_metadata)
            
            # Step 5: Store in ChromaDB
            rag = RAGService()
            collection = rag.get_collection()
            
            chunk_ids = []
            chunk_contents = []
            chunk_metadatas = []
            
            for chunk in chunks:
                chunk_ids.append(chunk["id"])
                chunk_contents.append(chunk["content"])
                chunk_metadatas.append(chunk["metadata"])
            
            # Add to ChromaDB in batch
            collection.add(
                ids=chunk_ids,
                documents=chunk_contents,
                metadatas=chunk_metadatas,
            )
            
            # Cleanup
            os.unlink(tmp_path)
            
            logger.info(f"Successfully stored {len(chunks)} chunks in ChromaDB")
            
            return {
                "status": "success",
                "subject": subject,
                "grade_level": grade_level,
                "chunks_created": len(chunks),
                "total_characters": len(cleaned_text),
                "filename": pdf_file.filename,
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {str(e)}")
            raise