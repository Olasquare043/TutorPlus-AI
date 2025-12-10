from fastapi import HTTPException, status


class TutorPlusException(Exception):
    """Base exception for TutorPlus"""
    pass


class UserNotFoundError(TutorPlusException):
    """Raised when user is not found"""
    pass


class InvalidCredentialsError(TutorPlusException):
    """Raised on authentication failure"""
    pass


class TokenExpiredError(TutorPlusException):
    """Raised when JWT token is expired"""
    pass


class InvalidTokenError(TutorPlusException):
    """Raised when JWT token is invalid"""
    pass


class AIServiceError(TutorPlusException):
    """Raised when AI service fails"""
    pass


class RAGError(TutorPlusException):
    """Raised when RAG operation fails"""
    pass


def http_exception_handler(status_code: int, detail: str) -> HTTPException:
    """Helper to create HTTP exceptions"""
    return HTTPException(status_code=status_code, detail=detail)