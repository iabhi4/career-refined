from http.client import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from utils.models import UserModel, WorkExperienceModel, EducationModel, ProjectModel, UserCreate, ApplicationModel
from config.database import get_db
from schemas import User, WorkExperience, Education, Project, Auth, Application

def get_auth_by_email(db: Session, email: str):
    """Get auth entry by email"""
    return db.query(Auth).filter(Auth.email == email).first()

def create_user(db: Session, user_data: UserCreate, hashed_password: str):
    """Create a new user with auth info"""

    auth = Auth(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        is_onboarded=False
    )
    db.add(auth)
    db.flush()  # Get auth_id

    # Then create user with auth_id
    db_user = User(
        auth_id=auth.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def onboard_user(db: Session, user_data: UserModel, user_id: int):
    """Onboard a new user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_data.dict().items():
        if isinstance(value, list):
            setattr(user, key, ", ".join(value) if value else None)
        elif value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user_id: int, user_data: UserModel):
    """Update user's profile details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_data.dict().items():
        if isinstance(value, list):
            setattr(user, key, ", ".join(value) if value else None)
        else:
            setattr(user, key, value)
    
    db.commit()
    return user

# Work Experience Operations
def add_work_experience(db: Session, user_id: int, work_exp: WorkExperienceModel):
    """Add work experience to a user profile"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_exp = WorkExperience(user_id=user_id, **work_exp.dict())
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return new_exp

def update_work_experience(db: Session, user_id: int, exp_id: int, work_exp: WorkExperienceModel):
    """Update work experience entry"""
    exp = db.query(WorkExperience).filter(
        WorkExperience.id == exp_id, 
        WorkExperience.user_id == user_id
    ).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Work experience not found")

    for key, value in work_exp.dict().items():
        setattr(exp, key, value)

    db.commit()
    return exp

# Education Operations
def add_education(db: Session, user_id: int, edu: EducationModel):
    """Add education to a user profile"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_edu = Education(user_id=user_id, **edu.dict())
    db.add(new_edu)
    db.commit()
    db.refresh(new_edu)
    return new_edu

def update_education(db: Session, user_id: int, edu_id: int, edu: EducationModel):
    """Update education entry"""
    education = db.query(Education).filter(
        Education.id == edu_id, 
        Education.user_id == user_id
    ).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")

    for key, value in edu.dict().items():
        setattr(education, key, value)

    db.commit()
    return education

# Project Operations
def add_project(db: Session, user_id: int, project: ProjectModel):
    """Add a project to a user profile"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_project = Project(user_id=user_id, **project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def update_project(db: Session, user_id: int, proj_id: int, project: ProjectModel):
    """Update project entry"""
    proj = db.query(Project).filter(
        Project.id == proj_id, 
        Project.user_id == user_id
    ).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.dict().items():
        setattr(proj, key, value)

    db.commit()
    return proj

# Helper Functions
def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_auth_by_email(db: Session, email: str):
    """Get auth entry by email"""
    return db.query(Auth).filter(Auth.email == email).first()


def get_user_skills(db: Session, user_id: int) -> list[str]:
    """Get only user's skills field"""
    query = select(User.skills).where(User.id == user_id)
    result = db.execute(query).scalar()
    
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return empty list if no skills, otherwise split and clean
    if not result:
        return []
    
    return [skill.strip() for skill in result.split(",")]

def get_work_experience_descriptions(db: Session, user_id: int) -> list[str]:
    """Get only work experience descriptions for a user"""
    query = select(WorkExperience.description).where(
        WorkExperience.user_id == user_id,
        WorkExperience.description.isnot(None)  # Only get non-null descriptions
    )
    
    results = db.execute(query).scalars().all()
    return list(results)

def get_project_descriptions(db: Session, user_id: int) -> list[str]:
    """Get only project descriptions for a user"""
    query = select(Project.description).where(
        Project.user_id == user_id,
        Project.description.isnot(None)  # Only get non-null descriptions
    )
    
    results = db.execute(query).scalars().all()
    return list(results)

def create_application(db: Session, application: ApplicationModel) -> ApplicationModel:
    """Create a new application"""
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
        return application
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error creating application"
        )
    
def update_user_onboarding_status(db: Session, user_id: int):
    """Update the onboarding status of a user to True"""
    auth_entry = db.query(Auth).join(User).filter(User.id == user_id).first()
    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    auth_entry.is_onboarded = True
    db.commit()
    return auth_entry