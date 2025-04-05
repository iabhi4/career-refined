from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger
from app.core.database import get_db
from app.schemas.user import User
from app.utils.auth import get_current_user
from app.crud.user import (
    get_user_by_id,
    update_user_profile,
    update_user_skills,
    update_user_languages,
    update_user_certifications,
    update_user_onboarding_status,
    add_work_experience,
    update_work_experience,
    delete_work_experience,
    add_education,
    update_education,
    delete_education,
    add_project,
    update_project,
    delete_project,
    get_profile_data,
    get_projects_and_experiences
)
from app.models.user import (
    UserModel, 
    UserResponse,
    SkillModel,
    LanguageModel,
    CertificationModel,
    PersonalDetailsUpdate,
)
from app.models.work_experience import WorkExperienceModel
from app.models.education import EducationModel
from app.models.project import ProjectModel

user = APIRouter()
logger = get_logger(__name__)

################# User Routes #################

@user.post("/users/{user_id}", response_model=UserResponse)
def create_user_route(user_data: UserModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new user."""
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    crud.onboard_user(db, user_data, user_id)
    auth_entry = update_user_onboarding_status(db, user_id)
    return {
        "user_id": auth_entry.id,
        "is_onboarded": auth_entry.is_onboarded
    }

@user.put("/users/{user_id}")
def update_user_route(user_id: int, user_data: PersonalDetailsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = update_user_profile(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}


@user.put("/users/{user_id}/skills")
def update_user_route(user_id: int, user_data: SkillModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = update_user_skills(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@user.put("/users/{user_id}/languages")
def update_user_route(user_id: int, user_data: LanguageModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = update_user_languages(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@user.put("/users/{user_id}/certifications")
def update_user_route(user_id: int, user_data: CertificationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user = update_user_certifications(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}


################# Work Experience Routes #################

@user.post("/users/{user_id}/work_experience")
def add_work_experience_route(user_id: int, work_exp: WorkExperienceModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add work experience to a user profile."""
    return add_work_experience(db, user_id, work_exp)

@user.put("/users/{user_id}/work_experience")
def update_work_experience_route(
    user_id: int, 
    work_exp: WorkExperienceModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work experience entry."""
    return update_work_experience(db, user_id, work_exp.company, work_exp)

@user.delete("/users/{user_id}/work_experience")
def delete_work_experience_route(user_id: int, company: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete work experience entry."""
    return delete_work_experience(db, user_id, company)

################# Education Routes #################

@user.post("/users/{user_id}/education")
def add_education_route(user_id: int, edu: EducationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add education to a user profile."""
    return add_education(db, user_id, edu)

@user.put("/users/{user_id}/education")
def update_education_route(
    user_id: int, 
    edu: EducationModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update education entry."""
    return update_education(db, user_id, edu.school_name, edu)

@user.delete("/users/{user_id}/education")
def delete_education_route(
    user_id: int, 
    school_name: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete education entry."""
    return delete_education(db, user_id, school_name)

################# Project Routes #################

@user.post("/users/{user_id}/projects")
def add_project_route(user_id: int, project: ProjectModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a project to a user profile."""
    return add_project(db, user_id, project)

@user.put("/users/{user_id}/projects")
def update_project_route(
    user_id: int, 
    project: ProjectModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project entry."""
    return update_project(db, user_id, project.project_name, project)

@user.delete("/users/{user_id}/projects")
def delete_project_route(user_id: int, project_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete project entry."""
    return delete_project(db, user_id, project_name)



@user.get("/users/{user_id}/profile-data/")
def get_profile_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get profile data for a user."""
    return get_profile_data(db, user_id)



@user.get("/users/{user_id}/projects-and-experiences/")
def get_projects_and_experiences(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get projects and experiences for a user."""
    logger.info(f"Fetching projects and experiences for user_id: {user_id}")
    try:
        projects_and_experiences = get_projects_and_experiences(db, user_id)
        logger.info(f"Successfully retrieved projects and experiences for user_id: {user_id}")
        return projects_and_experiences
    except Exception as e:
        logger.error(f"Error fetching projects and experiences for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching projects and experiences")