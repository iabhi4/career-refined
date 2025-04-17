from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger
from app.core.database import get_db
from app.schemas.user import User
from app.utils.auth import get_current_user
from app.crud import user
from app.services.rag.retriever import update_user_vector_index
from app.models.user import (
    UserModel, 
    UserResponse,
    SkillModel,
    LanguageModel,
    CertificationModel,
    PersonalDetailsUpdate,
    MessageOut
)
from app.models.work_experience import WorkExperienceModel
from app.models.education import EducationModel
from app.models.project import ProjectModel

user_router = APIRouter()
logger = get_logger(__name__)

################# User Routes #################

@user_router.post("/users/{user_id}", response_model=UserResponse)
def create_user_route(user_data: UserModel, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new user."""
    existing_user = user.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    user.onboard_user(db, user_data, user_id)
    auth_entry = user.update_user_onboarding_status(db, user_id)
    return {
        "user_id": auth_entry.id,
        "is_onboarded": auth_entry.is_onboarded
    }

@user_router.put("/users/{user_id}")
def update_user_route(user_id: int, user_data: PersonalDetailsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user_response = user.update_user_profile(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}


@user_router.put("/users/{user_id}/skills")
def update_user_route(user_id: int, user_data: SkillModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user_response = user.update_user_skills(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@user_router.put("/users/{user_id}/languages")
def update_user_route(user_id: int, user_data: LanguageModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user_response = user.update_user_languages(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}

@user_router.put("/users/{user_id}/certifications")
def update_user_route(user_id: int, user_data: CertificationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user's basic profile details."""
    user_response = user.update_user_certifications(db, user_id, user_data)
    return {"status": "Profile Updated successfully"}


################# Work Experience Routes #################

@user_router.post("/users/{user_id}/work_experience")
def add_work_experience_route(user_id: int, work_exp: WorkExperienceModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add work experience to a user profile."""
    return user.add_work_experience(db, user_id, work_exp)

@user_router.put("/users/{user_id}/work_experience")
def update_work_experience_route(
    user_id: int, 
    work_exp: WorkExperienceModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update work experience entry."""
    return user.update_work_experience(db, user_id, work_exp.company, work_exp)

@user_router.delete("/users/{user_id}/work_experience")
def delete_work_experience_route(user_id: int, company: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete work experience entry."""
    return user.delete_work_experience(db, user_id, company)

################# Education Routes #################

@user_router.post("/users/{user_id}/education")
def add_education_route(user_id: int, edu: EducationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add education to a user profile."""
    return user.add_education(db, user_id, edu)

@user_router.put("/users/{user_id}/education")
def update_education_route(
    user_id: int, 
    edu: EducationModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update education entry."""
    return user.update_education(db, user_id, edu.school_name, edu)

@user_router.delete("/users/{user_id}/education")
def delete_education_route(
    user_id: int, 
    school_name: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Delete education entry."""
    return user.delete_education(db, user_id, school_name)

################# Project Routes #################

@user_router.post("/users/{user_id}/projects")
def add_project_route(user_id: int, project: ProjectModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a project to a user profile."""
    return user.add_project(db, user_id, project)

@user_router.put("/users/{user_id}/projects")
def update_project_route(
    user_id: int, 
    project: ProjectModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project entry."""
    return user.update_project(db, user_id, project.project_name, project)

@user_router.delete("/users/{user_id}/projects")
def delete_project_route(user_id: int, project_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete project entry."""
    return user.delete_project(db, user_id, project_name)



@user_router.get("/users/{user_id}/profile-data/")
def get_profile_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get profile data for a user."""
    return user.get_profile_data(db, user_id)



@user_router.get("/users/{user_id}/projects-and-experiences/")
def get_projects_and_experiences(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get projects and experiences for a user."""
    logger.info(f"Fetching projects and experiences for user_id: {user_id}")
    try:
        projects_and_experiences = user.get_projects_and_experiences(db, user_id)
        logger.info(f"Successfully retrieved projects and experiences for user_id: {user_id}")
        return projects_and_experiences
    except Exception as e:
        logger.error(f"Error fetching projects and experiences for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching projects and experiences")
    

@user_router.post(
    "/users/{user_id}/embeddings",
    response_model=MessageOut,
    status_code=status.HTTP_200_OK,
    summary="(Re)build embeddings for a user",
    description="Fetches the latest profile data for `user_id`, splits it into docs, "
                "and writes all embeddings into ChromaDB under collection `user_profile_{user_id}`."
)
def rebuild_user_embeddings(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # — you may want to add an is_admin check here or ensure current_user.id == user_id
    try:
        update_user_vector_index(user_id=user_id, db=db, print_added_docs=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embeddings for user {user_id}: {e}"
        )
    return {"message": f"Embeddings for user {user_id} built successfully."}