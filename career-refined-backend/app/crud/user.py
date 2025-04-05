from http.client import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import (
    UserModel,
    UserCreate,
    PersonalDetailsUpdate,
    SkillModel,
    LanguageModel,
    CertificationModel,
)
from app.models.work_experience import WorkExperienceModel
from app.models.education import EducationModel
from app.models.project import ProjectModel
from app.schemas import User, WorkExperience, Education, Project, Auth
from app.core.logging_config import get_logger

logger = get_logger(__name__)

##############   AUTH CRUD OPERATIONS   ##############

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

def get_auth_by_email(db: Session, email: str):
    """Get auth entry by email"""
    return db.query(Auth).filter(Auth.email == email).first()

def update_user_onboarding_status(db: Session, user_id: int):
    """Update the onboarding status of a user to True"""
    auth_entry = db.query(Auth).join(User).filter(User.id == user_id).first()
    if not auth_entry:
        raise HTTPException(status_code=404, detail="User not found")

    auth_entry.is_onboarded = True
    db.commit()
    return auth_entry









###################   USER CRUD OPERATIONS   ##############

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

def update_user_profile(db: Session, user_id: int, user_data: PersonalDetailsUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only fields in PersonalDetailsUpdate can appear here
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    return user

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()









###### SKILL, LANGUAGE, CERTIFICATION CRUD OPERATIONS ######

def update_user_skills(db: Session, user_id: int, skills_data: SkillModel):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only fields in PersonalDetailsUpdate can appear here
    update_data = skills_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    return user

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

def update_user_languages(db: Session, user_id: int, language_data: LanguageModel):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only fields in PersonalDetailsUpdate can appear here
    update_data = language_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    return user

def update_user_certifications(db: Session, user_id: int, cert_data: CertificationModel):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only fields in PersonalDetailsUpdate can appear here
    update_data = cert_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    return user









############### WORK EXPERIENCE CRUD OPERATIONS ###############

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

def update_work_experience(db: Session, user_id: int, company: str, work_exp: WorkExperienceModel):
    """Update work experience entry"""
    logger.info(f"Updating work experience for user_id: {user_id}, company: {company}")
    try:
        exp = db.query(WorkExperience).filter(
            WorkExperience.company == company, 
            WorkExperience.user_id == user_id
        ).first()
        if not exp:
            logger.warning(f"Work experience not found for user_id: {user_id}, company: {company}")
            raise HTTPException(status_code=404, detail="Work experience not found")

        for key, value in work_exp.dict().items():
            setattr(exp, key, value)

        db.commit()
        logger.info(f"Successfully updated work experience for user_id: {user_id}, company: {company}")
        return exp
    except Exception as e:
        logger.error(f"Error updating work experience for user_id: {user_id}, company: {company}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating work experience")
    
def delete_work_experience(db: Session, user_id: int, company: str):
    """Delete work experience entry"""
    logger.info(f"Deleting work experience for user_id: {user_id}, company: {company}")
    try:
        exp = db.query(WorkExperience).filter(
            WorkExperience.company == company, 
            WorkExperience.user_id == user_id
        ).first()
        if not exp:
            logger.warning(f"Work experience not found for user_id: {user_id}, company: {company}")
            raise HTTPException(status_code=404, detail="Work experience not found")

        db.delete(exp)
        db.commit()
        logger.info(f"Successfully deleted work experience for user_id: {user_id}, company: {company}")
    except Exception as e:
        logger.error(f"Error deleting work experience for user_id: {user_id}, company: {company}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting work experience")
    
def get_work_experience_descriptions(db: Session, user_id: int) -> list[str]:
    """Get only work experience descriptions for a user"""
    query = select(WorkExperience.description).where(
        WorkExperience.user_id == user_id,
        WorkExperience.description.isnot(None)  # Only get non-null descriptions
    )
    
    results = db.execute(query).scalars().all()
    return list(results)
    








############### EDUCATION CRUD OPERATIONS ###############

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

def update_education(db: Session, user_id: int, school_name: str, edu: EducationModel):
    """Update education entry"""
    education = db.query(Education).filter(
        Education.school_name == school_name, 
        Education.user_id == user_id
    ).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")

    for key, value in edu.dict().items():
        setattr(education, key, value)

    db.commit()
    return education

def delete_education(db: Session, user_id: int, school_name: str):
    """Delete education entry"""
    logger.info(f"Deleting education for user_id: {user_id}, school_name: {school_name}")
    try:
        edu = db.query(Education).filter(
            Education.school_name == school_name, 
            Education.user_id == user_id
        ).first()
        if not edu:
            logger.warning(f"Education not found for user_id: {user_id}, school_name: {school_name}")
            raise HTTPException(status_code=404, detail="Education not found")

        db.delete(edu)
        db.commit()
        logger.info(f"Successfully deleted education for user_id: {user_id}, school_name: {school_name}")
    except Exception as e:
        logger.error(f"Error deleting education for user_id: {user_id}, school_name: {school_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting education")
    








############### PROJECT CRUD OPERATIONS ###############

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

def update_project(db: Session, user_id: int, project_name: str, project: ProjectModel):
    """Update project entry"""
    proj = db.query(Project).filter(
        Project.project_name == project_name, 
        Project.user_id == user_id
    ).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.dict().items():
        setattr(proj, key, value)

    db.commit()
    return proj

def delete_project(db: Session, user_id: int, project_name: str):
    """Delete project entry"""
    logger.info(f"Deleting project for user_id: {user_id}, project_name: {project_name}")
    try:
        proj = db.query(Project).filter(
            Project.project_name == project_name, 
            Project.user_id == user_id
        ).first()
        if not proj:
            logger.warning(f"Project not found for user_id: {user_id}, project_name: {project_name}")
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(proj)
        db.commit()
        logger.info(f"Successfully deleted project for user_id: {user_id}, project_name: {project_name}")
    except Exception as e:
        logger.error(f"Error deleting project for user_id: {user_id}, project_name: {project_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting project")
    
def get_project_descriptions(db: Session, user_id: int) -> list[str]:
    """Get only project descriptions for a user"""
    query = select(Project.description).where(
        Project.user_id == user_id,
        Project.description.isnot(None)  # Only get non-null descriptions
    )
    
    results = db.execute(query).scalars().all()
    return list(results)









############### MISC CRUD OPERATIONS ###############

def get_projects_and_experiences(db: Session, user_id: int):
    """Get projects and experiences for a user"""
    logger.info(f"Fetching projects and experiences for user {user_id}")  # Log the action
    try:
        projectQuery = select(Project.id, Project.project_name).where(Project.user_id == user_id)
        experienceQuery = select(WorkExperience.id, WorkExperience.company).where(WorkExperience.user_id == user_id)
        
        projectResults = db.execute(projectQuery).all()
        experienceResults = db.execute(experienceQuery).all()
        
        # Convert results to lists of dictionaries
        projects = [{"id": proj.id, "project_name": proj.project_name} for proj in projectResults]
        experiences = [{"id": exp.id, "company": exp.company} for exp in experienceResults]
        
        logger.info(f"Retrieved {len(projects)} projects and {len(experiences)} experiences for user {user_id}")  # Log the result count
        return {"projects": projects, "experiences": experiences}
    except Exception as e:
        logger.error(f"Error fetching projects and experiences for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching projects and experiences")

def get_profile_data(db: Session, user_id: int):
    """Get profile data for a user"""
    logger.info(f"Fetching profile data for user_id: {user_id}")
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        personalDetails = {
            "name": user.name,
            "location": user.location,
            "email": user.email,
            "phone_number": user.phone_number,
            "portfolio_link": user.portfolio_link,
            "linkedin_link": user.linkedin_link,
            "github_link": user.github_link,
        }
        workExperience = db.query(WorkExperience).filter(WorkExperience.user_id == user_id).all()
        experience = []
        for exp in workExperience:
            experience.append({
                "company": exp.company,
                "location": exp.location,
                "position": exp.position,
                "experience_type": exp.experience_type,
                "start_month": exp.start_month,
                "start_year": exp.start_year,
                "end_month": exp.end_month,
                "end_year": exp.end_year,
                "description": exp.description,
                "technologies_used": exp.technologies_used,
            })
        projects = db.query(Project).filter(Project.user_id == user_id).all()
        project = []
        for proj in projects:
            project.append({
                "project_name": proj.project_name,
                "company": proj.company,
                "location": proj.location,
                "position": proj.position,
                "experience_type": proj.experience_type,
                "technologies_used": proj.technologies_used,
                "start_month": proj.start_month,
                "start_year": proj.start_year,
                "end_month": proj.end_month,
                "end_year": proj.end_year,
                "project_link": proj.project_link,
                "description": proj.description,
            })
        education = db.query(Education).filter(Education.user_id == user_id).all()
        education_data = []
        for edu in education:
            education_data.append({
                "school_name": edu.school_name,
                "major": edu.major,
                "gpa": edu.gpa,
                "start_month": edu.start_month,
                "start_year": edu.start_year,
                "end_month": edu.end_month,
                "end_year": edu.end_year,  
                "degree_type": edu.degree_type,
            })
        editorData = {
            "personalDetails": personalDetails,
            "experience": experience,
            "projects": project,
            "skills": user.skills,
            "languages": user.languages,
            "certifications": user.certifications,
            "education": education_data,
        }
        return editorData
    except Exception as e:
        logger.error(f"Error fetching profile data for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching profile data")