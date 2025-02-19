from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.logging_config import get_logger
from config.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
import json
from datetime import datetime
from schemas.user import User
from schemas.auth import Auth
from services.nlp import analyze_job_description, compare_and_generate_suggestions, clean_job_description
from utils.auth import create_access_token, get_current_user, get_password_hash, authenticate_user, set_auth_cookie
from utils.utils import extract_relevant_items
from utils import crud
from utils.models import (
    UserModel, 
    WorkExperienceModel,
    EducationModel,
    ProjectModel,
    UserResponse,
    UserCreate,
    ApplicationAnalysisCreate,
    ApplicationAnalysisResponse,
    ApplicationModel,
    Token
)

router = APIRouter()
logger = get_logger(__name__)

################# User Routes #################

@router.post("/users/{user_id}", response_model=UserResponse)
def create_user_route(user_data: UserModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new user."""
    existing_user = crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    return crud.onboard_user(db, user_data, user_id)

@router.put("/users/{user_id}/", response_model=UserResponse)
def update_user_route(user_id: int, user_data: UserModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    return crud.update_user_profile(db, user_id, user_data)

################# Work Experience Routes #################

@router.post("/users/{user_id}/work_experience/")
def add_work_experience_route(work_exp: WorkExperienceModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add work experience to a user profile."""
    return crud.add_work_experience(db, user_id, work_exp)

@router.put("/users/{user_id}/work_experience/{exp_id}/")
def update_work_experience_route(
    user_id: int, 
    exp_id: int, 
    work_exp: WorkExperienceModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work experience entry."""
    return crud.update_work_experience(db, user_id, exp_id, work_exp)

################# Education Routes #################

@router.post("/users/{user_id}/education/")
def add_education_route(edu: EducationModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add education to a user profile."""
    return crud.add_education(db, user_id, edu)

@router.put("/users/{user_id}/education/{edu_id}/")
def update_education_route(
    user_id: int, 
    edu_id: int, 
    edu: EducationModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update education entry."""
    return crud.update_education(db, user_id, edu_id, edu)

################# Project Routes #################

@router.post("/users/{user_id}/projects/")
def add_project_route(project: ProjectModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a project to a user profile."""
    return crud.add_project(db, user_id, project)

@router.put("/users/{user_id}/projects/{proj_id}/")
def update_project_route(
    user_id: int, 
    proj_id: int, 
    project: ProjectModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project entry."""
    return crud.update_project(db, user_id, proj_id, project)

################# Resume Analysis Routes #################

@router.post("/applications/create-and-analyze")
async def create_and_analyze_application(
    application_data: ApplicationModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new application and analyze it:
    1. Create application record
    2. Clean and analyze job description
    3. Compare with resume
    4. Store analysis
    5. Return complete analysis
    """
    try:
        # Get application
        logger.info(f"Creating application for user {current_user.id}")
        application = crud.create_application(db, ApplicationModel(
            user_id=current_user.id,
            job_role=application_data.job_role,
            company=application_data.company,
            location=application_data.location,
            job_description=application_data.job_description,
            date_applied=datetime.utcnow(),
            application_status="Draft"
        ))

        # Step 1: Clean job description
        logger.info(f"Cleaning job description for application {application.id}")
        cleaned_description = clean_job_description(application.job_description)
        
        # Step 2: Extract keywords
        logger.info(f"Extracting keywords from cleaned description")
        keywords_response = analyze_job_description(cleaned_description)
        try:
            keywords = json.loads(keywords_response)['technical_keywords']
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=500, 
                detail="Error parsing keywords from analysis"
            )

        # Step 3: Get resume data for comparison
        logger.info(f"Getting resume data for user {current_user.id}")
        resume_data = {
            "skills": crud.get_user_skills(db, current_user.id),
            "experiences": crud.get_work_experience_descriptions(db, current_user.id),
            "projects": crud.get_project_descriptions(db, current_user.id)
        }

        # Step 4: Compare and get suggestions
        logger.info("Comparing keywords with resume data")
        comparison_response = compare_and_generate_suggestions(
            {"technical_keywords": keywords}, 
            resume_data
        )
        
        try:
            comparison_data = json.loads(comparison_response)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Error parsing comparison results"
            )

        # Extract relevant experience and project names from suggestions
        relevant_items = extract_relevant_items(comparison_data.get('suggestions', {}), resume_data['experiences'], resume_data['projects'])

        # Step 5: Create and store analysis
        analysis_data = ApplicationAnalysisCreate(
            job_description=cleaned_description,
            extracted_keywords=json.dumps(keywords),
            matched_keywords=json.dumps(comparison_data.get('matched_keywords', [])),
            missing_keywords=json.dumps(comparison_data.get('missing_keywords', [])),
            relevant_experiences=json.dumps(relevant_items['experiences']),
            relevant_projects=json.dumps(relevant_items['projects']),
            suggestions=json.dumps(comparison_data.get('suggestions', {}))
        )

        # Store in database
        logger.info(f"Storing analysis for application {application.id}")
        stored_analysis = crud.store_application_analysis(
            db, application.id, analysis_data
        )

        # Step 6: Return relevant data to frontend
        return {
            "matched_keywords": comparison_data.get('matched_keywords', []),
            "missing_keywords": comparison_data.get('missing_keywords', []),
            "relevant_experiences": relevant_items['experiences'],
            "relevant_projects": relevant_items['projects'],
            "suggestions": comparison_data.get('suggestions', {})
        }

    except Exception as e:
        logger.error(f"Error in application analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing application: {str(e)}"
        )

# @router.post("/extract_keywords/")
# def extract_job_keywords(request: str):
#     """API Endpoint to extract keywords from a job description."""
#     try:
#         logger.info(f"Received job description: {request}")
#         keywords = analyze_job_description(request)
#         return {"extracted_keywords": keywords}
#     except Exception as e:
#         logger.error(f"Error extracting keywords: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.post("/compare_resume/{user_id}/")
# def compare_resume_with_keywords(user_id: int, keywords: dict, db: Session = Depends(get_db)):
#     """Compare job keywords with user's resume and generate suggestions."""
#     try:
#         resume_data = {
#             "skills": crud.get_user_skills(db, user_id),
#             "experiences": crud.get_work_experience_descriptions(db, user_id),
#             "projects": crud.get_project_descriptions(db, user_id)
#         }

#         logger.info(f"Processing resume comparison for user {user_id}")
#         logger.debug(f"Resume data collected: {resume_data}")
#         logger.debug(f"Keywords to compare: {keywords}")

#         suggestions = compare_and_generate_suggestions(keywords, resume_data)
#         return {"suggestions": suggestions}
        
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Error comparing resume for user {user_id}: {str(e)}")
#         raise HTTPException(
#             status_code=500, 
#             detail="An error occurred while comparing resume"
#         )

################# Auth Routes #################

@router.post("/token", response_model=Token)
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
    set_auth_cookie(response, access_token)
    
    return response

@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user.email}")
    db_user = crud.get_auth_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Registration failed - email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    crud.create_user(db, user, hashed_password)
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
    set_auth_cookie(response, access_token)
    
    return response

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Request password reset."""
    return crud.handle_forgot_password(db, email)

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password using token."""
    return crud.handle_reset_password(db, token, new_password)

@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    return response

@router.get("/auth/me")
async def get_current_user(current_user: Auth = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_onboarded": current_user.is_onboarded
    }