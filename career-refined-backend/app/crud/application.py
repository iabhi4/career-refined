from http.client import HTTPException
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger
from app.models.application import ApplicationModel, ApplicationAnalysisCreate
from app.schemas import User, WorkExperience, Education, Project, Application, ApplicationAnalysis, CachedResume
from app.utils.helpers import categorize_skills

logger = get_logger(__name__)

##################### Application CRUD Operations #####################
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
            date_applied=application.date_applied,
            application_status=application.application_status,
            add_to_tracker=application.add_to_tracker
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
    
def get_tracker_data(db: Session, user_id: int):
    """Get tracker data for a user"""
    logger.info(f"Fetching tracker data for user_id: {user_id}")  # Log the action
    try:
        applications = db.query(Application).filter(
            Application.user_id == user_id,
            Application.add_to_tracker == True
        ).all()

        tracker_data = []
        for app in applications:
            analysis = db.query(ApplicationAnalysis).filter(
                ApplicationAnalysis.application_id == app.id
            ).first()

            tracker_data.append({
                "id": app.id,
                "job_role": app.job_role,
                "company": app.company,
                "location": app.location,
                "date_applied": app.date_applied,
                "application_status": app.application_status,
                "job_description": analysis.job_description if analysis else None,
                "extracted_keywords": analysis.extracted_keywords if analysis else None,
            })

        logger.info(f"Successfully fetched tracker data for user_id: {user_id}, total applications: {len(tracker_data)}")  # Log success
        return tracker_data
    except Exception as e:
        logger.error(f"Error fetching tracker data for user_id {user_id}: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Error fetching tracker data")
    
def add_manual_application(db: Session, user_id: int, application_data: ApplicationModel):
    """Add a manual application to the tracker"""
    logger.info(f"Adding manual application for user_id: {user_id}")  # Log the action
    try:
        new_application = Application(
            user_id=user_id,
            job_role=application_data.job_role,
            company=application_data.company,
            location=application_data.location,
            job_description=application_data.job_description,
            date_applied=application_data.date_applied,
            application_status=application_data.application_status,
            add_to_tracker=True  # Set this to True to add to tracker
        )
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        logger.info(f"Successfully added manual application for user_id: {user_id}, application_id: {new_application.id}")  # Log success
        return {
            "id": new_application.id,
            "job_role": new_application.job_role,
            "company": new_application.company,
            "location": new_application.location,
            "date_applied": new_application.date_applied,
            "application_status": new_application.application_status,
            "job_description": new_application.job_description,
        }
    except Exception as e:
        logger.error(f"Error adding manual application for user_id {user_id}: {e}")  # Log the error
        db.rollback()
        raise HTTPException(status_code=500, detail="Error adding manual application")    
    








############### Cached Resume CRUD Operations #####################

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






    


################## Editor Data CRUD Operations #####################
    
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