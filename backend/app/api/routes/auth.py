from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.user_service import UserService
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_token, get_user_id_from_token
from app.utils.exceptions import InvalidCredentialsError, UserNotFoundError, InvalidTokenError, TokenExpiredError
from app.api.dependencies import get_current_user
from app.models import User
from pydantic import BaseModel, EmailStr
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    pass


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **username**: Username (must be unique, 3-100 chars)
    - **password**: Password (minimum 8 characters)
    - **full_name**: User's full name (optional)
    - **preferred_language**: Language preference (en, yo, ha, ig)
    """
    try:
        user = UserService.create_user(db, user_create)
        logger.info(f"New user registered: {user.email}")
        return user
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    try:
        user = UserService.authenticate_user(
            db,
            login_request.email,
            login_request.password,
        )
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except InvalidCredentialsError as e:
        logger.warning(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = verify_token(refresh_request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")
        
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenError("Token does not contain user_id")
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_request.refresh_token,
            "token_type": "bearer",
        }
    except (InvalidTokenError, TokenExpiredError) as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout user (client-side should discard tokens)
    
    This is a placeholder endpoint. In production, you might want to:
    - Invalidate tokens in a blacklist (Redis)
    - Track logout events
    - Update user session status
    """
    logger.info(f"User logged out: {current_user.id}")
    
    return {
        "message": "Logged out successfully",
        "user_id": str(current_user.id),
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/verify-token", status_code=status.HTTP_200_OK)
async def verify_access_token(
    current_user: User = Depends(get_current_user),
):
    """
    Verify if access token is valid
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
    }