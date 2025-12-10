from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.password import hash_password, verify_password
from app.utils.exceptions import UserNotFoundError, InvalidCredentialsError
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations"""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_create.email) | (User.username == user_create.username)
        ).first()
        
        if existing_user:
            logger.warning(f"Attempt to create duplicate user: {user_create.email}")
            raise ValueError("Email or username already exists")
        
        # Hash password
        hashed_password = hash_password(user_create.password)
        
        # Create user
        user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            preferred_language=user_create.preferred_language,
            phone_number=user_create.phone_number,
            school_name=user_create.school_name,
            grade_level=user_create.grade_level,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created: {user.id}")
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        try:
            user = UserService.get_user_by_email(db, email)
        except UserNotFoundError:
            logger.warning(f"Authentication failed: user {email} not found")
            raise InvalidCredentialsError("Invalid email or password")
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for {email}")
            raise InvalidCredentialsError("Invalid email or password")
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user {email} is inactive")
            raise InvalidCredentialsError("User is inactive")
        
        logger.info(f"User authenticated: {user.id}")
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.id}")
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: UUID) -> User:
        """Deactivate a user account"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = False
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User deactivated: {user.id}")
        return user