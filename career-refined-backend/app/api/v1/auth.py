from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger
from app.core.database import get_db
from app.schemas.auth import Auth
from app.utils.auth import (
    create_access_token, 
    get_current_user, 
    get_password_hash, 
    authenticate_user, 
    set_auth_cookie
)
from app.crud.user import (
    get_auth_by_email,
    create_user,
)
from app.models.user import (
    UserCreate,
    Token,
)

auth_router = APIRouter()
logger = get_logger(__name__)


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint to get access token."""
    logger.info(f"Login attempt for email: {form_data.username}")
    auth_info = authenticate_user(db, form_data.username, form_data.password)
    if not auth_info:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": auth_info.email})
    logger.info(f"Successful login for user_id: {auth_info.id}, email: {auth_info.email}")
    
    response = JSONResponse(content={
        "user_id": auth_info.id,
        "is_onboarded": auth_info.is_onboarded
    })
    set_auth_cookie(response, access_token, auth_info.is_onboarded)
    
    return response

@auth_router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user.email}")
    db_user = get_auth_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Registration failed - email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    create_user(db, user, hashed_password)
    logger.info(f"User created successfully with email: {user.email}")
    
    auth_info = authenticate_user(db, user.email, user.password)
    if not auth_info:
        logger.error(f"Failed to authenticate newly created user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": auth_info.email})
    logger.info(f"Registration complete for user_id: {auth_info.id}, email: {auth_info.email}")
    
    response = JSONResponse(content={
        "user_id": auth_info.id,
        "is_onboarded": auth_info.is_onboarded
    })
    set_auth_cookie(response, access_token, auth_info.is_onboarded)
    
    return response

# @auth.post("/forgot-password")
# async def forgot_password(email: str, db: Session = Depends(get_db)):
#     """Request password reset."""
#     return handle_forgot_password(db, email)

# @auth.post("/reset-password")
# async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
#     """Reset password using token."""
#     return handle_reset_password(db, token, new_password)

@auth_router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response

@auth_router.get("/auth/me")
async def get_authenticated_user(current_user: Auth = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_onboarded": current_user.is_onboarded
    }