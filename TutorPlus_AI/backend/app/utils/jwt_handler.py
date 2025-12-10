from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.config import get_settings
from app.utils.exceptions import TokenExpiredError, InvalidTokenError
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token with extended expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise InvalidTokenError("Invalid token")


def get_user_id_from_token(token: str) -> str:
    """Extract user_id from token payload"""
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise InvalidTokenError("Token does not contain user_id")
    
    return user_id