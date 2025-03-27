from http.client import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from utils.models import UserModel, WorkExperienceModel, EducationModel, ProjectModel, UserCreate, ApplicationModel, ApplicationAnalysisCreate, PersonalDetailsUpdate, SkillModel, LanguageModel, CertificationModel
from config.database import get_db
from schemas import User, WorkExperience, Education, Project, Auth, Application, ApplicationAnalysis, CachedResume
from config.logging_config import get_logger
from utils.utils import categorize_skills

logger = get_logger(__name__)

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
        logger.info(f"Creating application for user {application.user_id}")
        new_application = Application(
            user_id=application.user_id,
            job_role=application.job_role,
            company=application.company,
            location=application.location,
            job_description=application.job_description,
        )
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        logger.info(f"Application created successfully for user {new_application.user_id}")
        return new_application
    except Exception as e:
        logger.error(f"Error creating application: {e}")
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

def store_application_analysis(db: Session, analysis_data: ApplicationAnalysisCreate):
    """Store application analysis data"""
    try:
        # Create a new analysis entry
        logger.info(f"Storing application analysis for application {analysis_data.application_id}")
        new_analysis = ApplicationAnalysis(
            user_id=analysis_data.user_id,
            application_id=analysis_data.application_id,
            job_description=analysis_data.job_description,
            extracted_keywords=analysis_data.extracted_keywords,
            matched_keywords=analysis_data.matched_keywords,
            missing_keywords=analysis_data.missing_keywords,
            relevant_experiences=analysis_data.relevant_experiences,
            relevant_projects=analysis_data.relevant_projects,
            suggestions=analysis_data.suggestions
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        logger.info(f"Application analysis stored successfully for application {analysis_data.application_id}")
        return new_analysis
    except Exception as e:
        logger.error(f"Error storing application analysis: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error storing application analysis"
        )

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
        
        
        
def get_cached_resume(db: Session, user_id: int):
    """Get cached resume for a user"""
    logger.info(f"Fetching cached resume for user_id: {user_id}")  # Log the action
    try:
        resume = db.query(CachedResume).filter(CachedResume.user_id == user_id).first()
        if not resume:
            logger.warning(f"No cached resume found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="Cached resume not found")
        logger.info(f"Successfully retrieved cached resume for user_id: {user_id}")
        return resume
    except Exception as e:
        logger.error(f"Error fetching cached resume for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching cached resume")
    

def cached_resume_exists(db: Session, user_id: int) -> bool:
    """Check if a cached resume exists for a user"""
    logger.info(f"Fetching cached resume for user_id: {user_id}")  # Log the action
    try:
        resume = db.query(CachedResume).filter(CachedResume.user_id == user_id).first()
        if not resume:
            logger.warning(f"No cached resume found for user_id: {user_id}")
            return False
        logger.info(f"Cached resume found for user_id: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error fetching cached resume for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching cached resume")
        

def get_editor_data_for_first_time(db: Session, user_id: int, exps: list[int], projects: list[int]):
    """Get editor data for a user"""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        personalDetails = {
            "name": user.name,
            "phone": user.phone_number,
            "email": user.email,
            "linkedin": user.linkedin_link,
            "github": user.github_link,
        }
        workExperience = db.query(WorkExperience).filter(WorkExperience.id.in_(exps)).all()
        experience = []
        for exp in workExperience:
            experience.append({
                "company": exp.company,
                "startDate": exp.start_month + " " + str(exp.start_year),
                "endDate": exp.end_month + " " + str(exp.end_year),
                "role": exp.position,
                "location": exp.location,
                "responsibilities": exp.description,
            })
        projects = db.query(Project).filter(Project.id.in_(projects)).all()
        project = []
        for proj in projects:
            project.append({
                "name": proj.project_name,
                "technologies": proj.technologies_used,
                "startDate": proj.start_month + " " + str(proj.start_year),
                "endDate": proj.end_month + " " + str(proj.end_year),
                "description": proj.description,
            })
        education = db.query(Education).filter(Education.user_id == user_id).all()
        education_data = []
        for edu in education:
            education_data.append({
                "institution": edu.school_name,
                "startYear": edu.start_month + " " + str(edu.start_year),
                "endYear": edu.end_month + " " + str(edu.end_year),
                "major": edu.major,   
                "degree": edu.degree_type,
            })
        editorData = {
            "personalDetails": personalDetails,
            "experience": experience,
            "projects": project,
            "skills": categorize_skills(user.skills),
            "education": education_data,
        }
        return editorData
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")

def update_editor_data(db: Session, user_id: int, editor_data: str):
    """Update editor data for a user"""
    logger.info(f"Updating editor data for user_id: {user_id}")
    try:
        cached_resume = db.query(CachedResume).filter(CachedResume.user_id == user_id).first()
        if not cached_resume:
            raise HTTPException(status_code=404, detail="Cached resume not found")
        
        # Update the editor_content column with the new value
        cached_resume.editor_content = editor_data  # Assuming editor_data has an editor_content attribute
        db.commit()
        return cached_resume
    except Exception as e:
        logger.error(f"Error updating editor data for user_id {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating editor data")
    

def create_cached_resume(db: Session, user_id: int, resume_data: str):
    """Cache a user's resume data"""
    logger.info(f"Caching resume for user_id: {user_id}")
    try:
        cached_resume = CachedResume(user_id=user_id, editor_content=resume_data, pdf_url="/Abhinav_Singh.pdf")
        db.add(cached_resume)
        db.commit()
        db.refresh(cached_resume)
        logger.info(f"Successfully cached resume for user_id: {user_id}")
        return cached_resume
    except Exception as e:
        logger.error(f"Error caching resume for user_id {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error caching resume")


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









