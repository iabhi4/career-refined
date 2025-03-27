from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.logging_config import get_logger
from config.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
import json
from datetime import datetime
from schemas.user import User
from schemas.auth import Auth
from services.latex import generate_resume_latex, compile_latex
from celery.result import AsyncResult
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
    Token,
    EditorModel,
    SkillModel,
    LanguageModel,
    CertificationModel,
    PersonalDetailsUpdate,
    ResumeDataModel,
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
    crud.onboard_user(db, user_data, user_id)
    auth_entry = crud.update_user_onboarding_status(db, user_id)
    return {
        "user_id": auth_entry.id,
        "is_onboarded": auth_entry.is_onboarded
    }

@router.put("/users/{user_id}")
def update_user_route(user_id: int, user_data: PersonalDetailsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = crud.update_user_profile(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}


@router.put("/users/{user_id}/skills")
def update_user_route(user_id: int, user_data: SkillModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = crud.update_user_skills(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@router.put("/users/{user_id}/languages")
def update_user_route(user_id: int, user_data: LanguageModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = crud.update_user_languages(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@router.put("/users/{user_id}/certifications")
def update_user_route(user_id: int, user_data: CertificationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = crud.update_user_certifications(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

################# Work Experience Routes #################

@router.post("/users/{user_id}/work_experience")
def add_work_experience_route(user_id: int, work_exp: WorkExperienceModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add work experience to a user profile."""
    return crud.add_work_experience(db, user_id, work_exp)

@router.put("/users/{user_id}/work_experience")
def update_work_experience_route(
    user_id: int, 
    work_exp: WorkExperienceModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work experience entry."""
    return crud.update_work_experience(db, user_id, work_exp.company, work_exp)

################# Education Routes #################

@router.post("/users/{user_id}/education")
def add_education_route(user_id: int, edu: EducationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add education to a user profile."""
    return crud.add_education(db, user_id, edu)

@router.put("/users/{user_id}/education")
def update_education_route(
    user_id: int, 
    edu: EducationModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update education entry."""
    return crud.update_education(db, user_id, edu.school_name, edu)

################# Project Routes #################

@router.post("/users/{user_id}/projects")
def add_project_route(user_id: int, project: ProjectModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a project to a user profile."""
    return crud.add_project(db, user_id, project)

@router.put("/users/{user_id}/projects")
def update_project_route(
    user_id: int, 
    project: ProjectModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project entry."""
    return crud.update_project(db, user_id, project.project_name, project)

################# Application Routes #################


@router.get("/users/{user_id}/profile-data/")
def get_profile_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get profile data for a user."""
    return crud.get_profile_data(db, user_id)



@router.get("/users/{user_id}/projects-and-experiences/")
def get_projects_and_experiences(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get projects and experiences for a user."""
    logger.info(f"Fetching projects and experiences for user_id: {user_id}")
    try:
        projects_and_experiences = crud.get_projects_and_experiences(db, user_id)
        logger.info(f"Successfully retrieved projects and experiences for user_id: {user_id}")
        return projects_and_experiences
    except Exception as e:
        logger.error(f"Error fetching projects and experiences for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching projects and experiences")
    
@router.get("/users/{user_id}/editor-data/")
def get_editor_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        cached_resume = crud.get_cached_resume(db, user_id)
        return {"editorContent" : cached_resume.editor_content, "pdfUrl" : cached_resume.pdf_url}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

@router.put("/users/{user_id}/editor-data")
def update_resume_pdf(user_id: int, editor_data: ResumeDataModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Updating resume PDF for user_id: {user_id}")
    try:
        cached_resume = crud.cached_resume_exists(db, user_id)
        editor_content = editor_data.json()
        if not cached_resume:
            logger.info(f"No cached resume found for user_id: {user_id}. Creating new cached resume.")
            crud.create_cached_resume(db, user_id, editor_content)
        else:
            logger.info(f"Cached resume found for user_id: {user_id}. Updating editor data.")
            crud.update_editor_data(db, user_id, editor_content)
        
        # Generate LaTeX file from editor_data
        latex_filepath = generate_resume_latex(editor_data)
        
        # Enqueue Celery task
        task = compile_latex.delay(latex_filepath)
        logger.info(f"Enqueued LaTeX compilation task for user_id: {user_id} with task id: {task.id}")
        # Return task id so the client can poll the status later.
        return {"task_id": task.id}
    except Exception as e:
        logger.error(f"Error updating resume PDF for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating resume PDF")
    

@router.get("/editor-data/pdf-status/{task_id}")
def get_resume_pdf_status(task_id: str, current_user: User = Depends(get_current_user)):
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"state": task_result.state, "status": "Pending..."}
    elif task_result.state == "SUCCESS":
        pdf_path = task_result.result  # This is the compiled PDF file path
        return {"state": task_result.state, "pdf_path": pdf_path}
    elif task_result.state == "FAILURE":
        return {"state": task_result.state, "error": str(task_result.info)}
    else:
        return {"state": task_result.state, "status": "Processing..."}


@router.get("/users/{user_id}/editor-data-new/")
def get_editor_data_new(user_id: int, exps: List[int] = Query(..., alias="exps[]"),
    projects: List[int] = Query(..., alias="projects[]"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        editor_data = crud.get_editor_data_for_first_time(db, user_id, exps, projects)
        #now once this json is returned, we will create the pdf file by creating a latex file and then we will compile it to return the pdf url
        logger.info(f"Successfully retrieved editor data for user_id: {user_id}")

        return {"editorContent" : editor_data, "pdfUrl" : "/Abhinav_Singh.pdf"}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

################# Resume Analysis Routes #################

@router.post("/applications/create-and-analyze/")
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
        logger.info(f"Creating application for user {application_data.user_id}")
        application = crud.create_application(db, ApplicationModel(
            user_id=application_data.user_id,
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
            logger.info(f"Keywords response: {keywords_response}")
            #keywords = json.loads(keywords_response)['technical_keywords']
            keywords = json.loads(keywords_response)
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(
                status_code=500, 
                detail="Error parsing keywords from analysis"
            )

        # Step 3: Get resume data for comparison
        logger.info(f"Getting resume data for user {application_data.user_id}")
        resume_data = {
            "skills": crud.get_user_skills(db, application_data.user_id),
            "experiences": crud.get_work_experience_descriptions(db, application_data.user_id),
            "projects": crud.get_project_descriptions(db, application_data.user_id)
        }

        # Step 4: Compare and get suggestions
        logger.info("Comparing keywords with resume data")
        comparison_response = compare_and_generate_suggestions(
            {"technical_keywords": keywords}, 
            resume_data
        )
        
        try:
            logger.info(f"Comparison response: {comparison_response}")
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
            user_id=application_data.user_id,
            application_id=application.id,
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
            db, analysis_data
        )

        # Step 6: Return relevant data to frontend
        return {
            "extracted_keywords": keywords,
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
    set_auth_cookie(response, access_token, auth_info.is_onboarded)
    
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
async def get_authenticated_user(current_user: Auth = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_onboarded": current_user.is_onboarded
    }