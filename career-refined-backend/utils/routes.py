from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.logging_config import get_logger
from config.db import get_db
from utils import schema
from utils.models import UserSchema, WorkExperienceSchema, EducationSchema, ProjectSchema

router = APIRouter()
logger = get_logger(__name__)

@router.post("/users/")
def create_user(user_data: UserSchema, db: Session = Depends(get_db)):
    """Create a new user."""
    existing_user = db.query(schema.User).filter(schema.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = schema.User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        location=user_data.location,
        resume=user_data.resume,
        portfolio_link=user_data.portfolio_link,
        linkedin_link=user_data.linkedin_link,
        github_link=user_data.github_link,
        skills=", ".join(user_data.skills) if user_data.skills else None,
        languages=", ".join(user_data.languages) if user_data.languages else None,
        certifications=", ".join(user_data.certifications) if user_data.certifications else None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@router.put("/users/{user_id}/")
def update_user(user_id: int, user_data: UserSchema, db: Session = Depends(get_db)):
    """Update user's basic profile details."""
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_data.name
    user.phone_number = user_data.phone_number
    user.location = user_data.location
    user.resume = user_data.resume
    user.portfolio_link = user_data.portfolio_link
    user.linkedin_link = user_data.linkedin_link
    user.github_link = user_data.github_link
    user.skills = ", ".join(user_data.skills) if user_data.skills else None
    user.languages = ", ".join(user_data.languages) if user_data.languages else None
    user.certifications = ", ".join(user_data.certifications) if user_data.certifications else None

    db.commit()
    return {"message": "User profile updated successfully"}


@router.post("/users/{user_id}/work_experience/")
def add_work_experience(user_id: int, work_exp: WorkExperienceSchema, db: Session = Depends(get_db)):
    """Add work experience to a user profile."""
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_exp = schema.WorkExperience(user_id=user_id, **work_exp.dict())
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return {"message": "Work experience added successfully", "work_experience_id": new_exp.id}



@router.put("/users/{user_id}/work_experience/{exp_id}/")
def update_work_experience(user_id: int, exp_id: int, work_exp: WorkExperienceSchema, db: Session = Depends(get_db)):
    """Update work experience entry."""
    exp = db.query(schema.WorkExperience).filter(schema.WorkExperience.id == exp_id, schema.WorkExperience.user_id == user_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Work experience not found")

    for key, value in work_exp.dict().items():
        setattr(exp, key, value)

    db.commit()
    return {"message": "Work experience updated successfully"}



@router.post("/users/{user_id}/education/")
def add_education(user_id: int, edu: EducationSchema, db: Session = Depends(get_db)):
    """Add education to a user profile."""
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_edu = schema.Education(user_id=user_id, **edu.dict())
    db.add(new_edu)
    db.commit()
    db.refresh(new_edu)
    return {"message": "Education added successfully", "education_id": new_edu.id}


@router.put("/users/{user_id}/education/{edu_id}/")
def update_education(user_id: int, edu_id: int, edu: EducationSchema, db: Session = Depends(get_db)):
    """Update education entry."""
    education = db.query(schema.Education).filter(schema.Education.id == edu_id, schema.Education.user_id == user_id).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")

    for key, value in edu.dict().items():
        setattr(education, key, value)

    db.commit()
    return {"message": "Education updated successfully"}


@router.post("/users/{user_id}/projects/")
def add_project(user_id: int, project: ProjectSchema, db: Session = Depends(get_db)):
    """Add a project to a user profile."""
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_project = schema.Project(user_id=user_id, **project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": "Project added successfully", "project_id": new_project.id}

@router.put("/users/{user_id}/projects/{proj_id}/")
def update_project(user_id: int, proj_id: int, project: ProjectSchema, db: Session = Depends(get_db)):
    """Update project entry."""
    proj = db.query(schema.Project).filter(schema.Project.id == proj_id, schema.Project.user_id == user_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.dict().items():
        setattr(proj, key, value)

    db.commit()
    return {"message": "Project updated successfully"}