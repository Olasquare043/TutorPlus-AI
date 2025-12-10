import chromadb
from app.config import get_settings
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """Service for RAG operations using ChromaDB"""
    
    _instance = None
    _client = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls):
        """Initialize ChromaDB client and collection"""
        if cls._client is not None:
            logger.info("ChromaDB already initialized")
            return
        
        try:
            logger.info(f"Initializing ChromaDB with persist_dir: {settings.chroma_persist_dir}")
            
            # Use chromadb.PersistentClient for persistent storage
            cls._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            
            # Get or create collection
            cls._collection = cls._client.get_or_create_collection(
                name="syllabus",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    @classmethod
    def get_collection(cls):
        """Get the ChromaDB collection"""
        if cls._client is None:
            # Re-initialize if for some reason the client is None (e.g., during testing or if the app restarts)
            cls.initialize()
        return cls._collection
    
    @staticmethod
    def add_syllabus_content(
        subject: str,
        topic: str,
        content: str,
        subtopic: Optional[str] = None,
        difficulty_level: str = "medium"
    ) -> str:
        """Add syllabus content to RAG collection"""
        
        try:
            logger.info(f"Adding syllabus content: {subject} - {topic}")
            
            collection = RAGService.get_collection()
            
            # Create unique ID
            doc_id = str(uuid.uuid4())
            
            # Prepare metadata
            metadata = {
                "subject": subject,
                "topic": topic,
                "subtopic": subtopic or "general",
                "difficulty_level": difficulty_level,
            }
            
            # Add to collection
            collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata],
            )
            
            logger.info(f"Syllabus content added with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add syllabus content: {str(e)}")
            raise
    
    @staticmethod
    def search_syllabus(
        query: str,
        subject: Optional[str] = None,
        top_k: int = 3
    ) -> List[dict]:
        """Search syllabus content using RAG"""
        
        try:
            logger.info(f"Searching syllabus for: {query}")
            
            collection = RAGService.get_collection()
            
            # Build where filter if subject is specified
            where_filter = None
            if subject:
                where_filter = {"subject": {"$eq": subject}}
            
            # Query
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
            )
            
            # Format results
            formatted_results = []
            if results and results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "id": results["ids"][0][i] if results["ids"] else None,
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None,
                    })
            
            logger.info(f"Found {len(formatted_results)} relevant documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Syllabus search failed: {str(e)}")
            return []
    
    @staticmethod
    def batch_add_syllabus(syllabi: List[dict]) -> List[str]:
        """Add multiple syllabus items at once"""
        
        ids = []
        for syllabus_item in syllabi:
            try:
                doc_id = RAGService.add_syllabus_content(
                    subject=syllabus_item.get("subject"),
                    topic=syllabus_item.get("topic"),
                    content=syllabus_item.get("content"),
                    subtopic=syllabus_item.get("subtopic"),
                    difficulty_level=syllabus_item.get("difficulty_level", "medium"),
                )
                ids.append(doc_id)
            except Exception as e:
                logger.error(f"Failed to add syllabus item: {str(e)}")
                continue
        
        return ids