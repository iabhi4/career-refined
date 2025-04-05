import os, json
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from app.core.logging_config import get_logger
from app.core.database import get_db
from app.schemas.user import User
from app.services.latex import generate_resume_latex, compile_latex
from app.celery_app import celery_app
from app.services.nlp import analyze_job_description, compare_and_generate_suggestions, clean_job_description
from app.utils.auth import get_current_user
from app.utils.helpers import extract_relevant_items
from app.crud.application import (
    get_cached_resume,
    cached_resume_exists,
    create_cached_resume,
    update_editor_data,
    get_editor_data_for_first_time,
    get_tracker_data,
    add_manual_application,
    create_application,
    store_application_analysis,
)
from app.crud.user import (
    get_user_skills,
    get_work_experience_descriptions,
    get_project_descriptions,
)
from app.models.application import (
    ApplicationAnalysisCreate,
    ApplicationModel,
)
from app.models.user import ResumeDataModel

application = APIRouter()
logger = get_logger(__name__)


@application.get("/users/{user_id}/editor-data")
def get_editor_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        cached_resume = get_cached_resume(db, user_id)
        return {"editorContent" : cached_resume.editor_content, "pdfUrl" : cached_resume.pdf_url}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

@application.put("/users/{user_id}/editor-data")
def update_resume_pdf(user_id: int, editor_data: ResumeDataModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Updating resume PDF for user_id: {user_id}")
    try:
        cached_resume = cached_resume_exists(db, user_id)
        editor_content = editor_data.json()
        if not cached_resume:
            logger.info(f"No cached resume found for user_id: {user_id}. Creating new cached resume.")
            create_cached_resume(db, user_id, editor_content)
        else:
            logger.info(f"Cached resume found for user_id: {user_id}. Updating editor data.")
            update_editor_data(db, user_id, editor_content)
        
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
    

@application.get("/editor-data/pdf-status/{task_id}")
def get_resume_pdf_status(task_id: str, current_user: User = Depends(get_current_user)):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == "PENDING":
        return {"state": task_result.state, "status": "Pending..."}
    elif task_result.state == "SUCCESS":
        pdf_path = task_result.result  # This is the compiled PDF file path
        return {"state": task_result.state, "pdf_path": pdf_path}
    elif task_result.state == "FAILURE":
        return {"state": task_result.state, "error": str(task_result.info)}
    else:
        return {"state": task_result.state, "status": "Processing..."}
    

@application.get("/download-pdf/{user_id}/{filename}")
async def download_pdf(user_id: int, filename: str, current_user: User = Depends(get_current_user)):
    """Download the generated PDF file."""
    pdf_path = os.path.join("pdfs", filename)
    # Potentially add checks or authentication here
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )


@application.get("/users/{user_id}/editor-data-new/")
def get_editor_data_new(user_id: int, exps: List[int] = Query(..., alias="exps[]"),
    projects: List[int] = Query(..., alias="projects[]"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        editor_data = get_editor_data_for_first_time(db, user_id, exps, projects)
        #now once this json is returned, we will create the pdf file by creating a latex file and then we will compile it to return the pdf url
        logger.info(f"Successfully retrieved editor data for user_id: {user_id}")

        return {"editorContent" : editor_data, "pdfUrl" : "/Abhinav_Singh.pdf"}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

################# Application tracker Routes #################
@application.get("/users/{user_id}/tracker-data")
def get_tracker_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch tracker data for a user."""
    logger.info(f"Fetching tracker data for user_id: {user_id}")
    try:
        tracker_data = get_tracker_data(db, user_id)
        logger.info(f"Successfully retrieved tracker data for user_id: {user_id}")
        return tracker_data
    except Exception as e:
        logger.error(f"Error fetching tracker data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tracker data")



@application.post("/users/{user_id}/manual-application")
def add_manual_application(user_id: int, application_data: ApplicationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a manual application to the user's tracker."""
    logger.info(f"Adding manual application for user_id: {user_id}")
    try:
        new_application = add_manual_application(db, user_id, application_data)
        logger.info(f"Successfully added manual application for user_id: {user_id}")
        return new_application
    except Exception as e:
        logger.error(f"Error adding manual application for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding manual application")





    

################# Resume Analysis Routes #################

@application.post("/applications/create-and-analyze/")
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
        application = create_application(db, ApplicationModel(
            user_id=application_data.user_id,
            job_role=application_data.job_role,
            company=application_data.company,
            location=application_data.location,
            job_description=application_data.job_description,
            date_applied=datetime.utcnow(),
            application_status="Draft",
            add_to_tracker=application_data.add_to_tracker
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
            "skills": get_user_skills(db, application_data.user_id),
            "experiences": get_work_experience_descriptions(db, application_data.user_id),
            "projects": get_project_descriptions(db, application_data.user_id)
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
        stored_analysis = store_application_analysis(
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