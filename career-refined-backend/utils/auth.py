from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config.database import get_db
from utils.crud import get_auth_by_email
from config.settings import settings
from fastapi.responses import JSONResponse
from schemas.auth import Auth
from utils.models import TokenData
from config.logging_config import get_logger

logger = get_logger(__name__)
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Auth:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not access_token:
        raise credentials_exception
        
    try:
        # Remove "Bearer " prefix if it exists
        token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(Auth).filter(Auth.email == token_data.email).first()
    if user is None:
        raise credentials_exception
        
    return user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user using the new Auth table"""
    logger.info(f"Attempting to authenticate user with email: {email}")
    auth_info = get_auth_by_email(db, email)
    if not auth_info:
        logger.warning(f"Authentication failed: User with email {email} not found")
        return False
    if not verify_password(password, auth_info.hashed_password):
        logger.warning(f"Authentication failed: Incorrect password for email {email}")
        return False
    logger.info(f"User with email {email} authenticated successfully")
    return auth_info

def set_auth_cookie(response: JSONResponse, token: str, is_onboarded: bool) -> None:
    """Helper function to set authentication cookie consistently."""
    # Set the access_token cookie (usually HTTP-only)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=True,  # for HTTPS
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # convert minutes to seconds
    )

    # Set the is_onboarded cookie (usually NOT HTTP-only so the client can read it)
    response.set_cookie(
        key="is_onboarded",
        value="true" if is_onboarded else "false",
        httponly=False,   # allow reading on client side
        secure=True,      # for HTTPS
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
