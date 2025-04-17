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
from app.services.latex.generator import generate_resume_latex
from app.services.latex.tasks import compile_latex
from app.celery_app import celery_app
from app.services.nlp import analyze_job_description, compare_and_generate_suggestions, clean_job_description
from app.utils.auth import get_current_user
from app.utils.helpers import extract_relevant_items, calculate_matched_missing, merge_editor_data
from app.services.rag.generation import generate_combined_rag_output
from app.crud import application
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

application_router = APIRouter()
logger = get_logger(__name__)


@application_router.get("/users/{user_id}/editor-data")
def get_editor_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        cached_resume = application.get_cached_resume(db, user_id)
        editor_content_dict = json.loads(cached_resume.editor_content)
        latex_filepath = generate_resume_latex(editor_content_dict)

        # Enqueue Celery task
        logger.info(f"Enqueuing LaTeX compilation task for user_id {user_id}")
        task = compile_latex.delay(latex_filepath)
        logger.info(f"Enqueued LaTeX compilation task | Task ID: {task.id}")
        
        return {"editorContent": cached_resume.editor_content, "taskId": task.id}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

@application_router.get("/editor-data/pdf-status/{task_id}")
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
    

@application_router.get("/download-pdf/{user_id}/{filename}")
async def download_pdf(user_id: int, filename: str, current_user: User = Depends(get_current_user)):
    """Download the generated PDF file."""
    pdf_path = os.path.join("pdfs", filename)
    # Potentially add checks or authentication here
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )


@application_router.get("/users/{user_id}/editor-data-new/")
def get_editor_data_new(user_id: int, exps: List[int] = Query(..., alias="exps[]"),
    projects: List[int] = Query(..., alias="projects[]"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get editor data for a user."""
    logger.info(f"Fetching editor data for user_id: {user_id}")
    try:
        editor_data = application.get_editor_data_for_first_time(db, user_id, exps, projects)
        #now once this json is returned, we will create the pdf file by creating a latex file and then we will compile it to return the pdf url
        logger.info(f"Successfully retrieved editor data for user_id: {user_id}")

        return {"editorContent" : editor_data, "pdfUrl" : "/Abhinav_Singh.pdf"}
    except Exception as e:
        logger.error(f"Error fetching editor data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching editor data")
    

################# Application tracker Routes #################
@application_router.get("/users/{user_id}/tracker-data")
def get_tracker_data(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch tracker data for a user."""
    logger.info(f"Fetching tracker data for user_id: {user_id}")
    try:
        tracker_data = application.get_tracker_data(db, user_id)
        logger.info(f"Successfully retrieved tracker data for user_id: {user_id}")
        return tracker_data
    except Exception as e:
        logger.error(f"Error fetching tracker data for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tracker data")



@application_router.post("/users/{user_id}/manual-application")
def add_manual_application(user_id: int, application_data: ApplicationModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add a manual application to the user's tracker."""
    logger.info(f"Adding manual application for user_id: {user_id}")
    try:
        new_application = application.add_manual_application(db, user_id, application_data)
        logger.info(f"Successfully added manual application for user_id: {user_id}")
        return new_application
    except Exception as e:
        logger.error(f"Error adding manual application for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding manual application")





    

################# Resume Analysis Routes #################

@application_router.post("/applications/create-and-analyze/")
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
        application_response = application.create_application(db, ApplicationModel(
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
        logger.info(f"Cleaning job description for application {application_response.id}")
        cleaned_description = clean_job_description(application_response.job_description)
        
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
            application_id=application_response.id,
            job_description=cleaned_description,
            extracted_keywords=json.dumps(keywords),
            matched_keywords=json.dumps(comparison_data.get('matched_keywords', [])),
            missing_keywords=json.dumps(comparison_data.get('missing_keywords', [])),
            relevant_experiences=json.dumps(relevant_items['experiences']),
            relevant_projects=json.dumps(relevant_items['projects']),
            suggestions=json.dumps(comparison_data.get('suggestions', {}))
        )

        # Store in database
        logger.info(f"Storing analysis for application {application_response.id}")
        stored_analysis = application.store_application_analysis(
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
    

@application_router.post("/applications/new-analysis")
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
        application_response = application.create_application(db, ApplicationModel(
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
        logger.info(f"Cleaning job description for application {application_response.id}")
        cleaned_description = clean_job_description(application_response.job_description)
        
        # Step 2: Extract keywords
        logger.info(f"Extracting keywords from cleaned description")

        rag_result = generate_combined_rag_output(
            user_id=application_data.user_id,
            job_description=application_data.job_description
        )

        if not rag_result:
            logger.error("RAG generation failed to produce results.")
            raise Exception("RAG generation failed to produce results.")
        
        try:
            logger.info(f"RAG RESULT response: {rag_result}")
        except (json.JSONDecodeError, KeyError):
            logger.error("Error parsing RAG result.")
            raise HTTPException(
                status_code=500, 
                detail="Error parsing keywords from analysis"
            )

        # Ensure expected keys exist (adjust based on your final RAG output schema)
        tailored_resume = rag_result.get("tailored_resume")
        extracted_keywords_data = rag_result.get("extracted_keywords", {})
        suggestions = rag_result.get("improvement_feedback")
        logger.info(f"I'm hereeeeeeeeee: {extracted_keywords_data}")  # Or "improvement_feedback" depending on your prompt
        if not tailored_resume or not extracted_keywords_data or not suggestions:
            logger.error("RAG output missing expected top-level keys.")
            raise ValueError("RAG output missing expected top-level keys.")

        extracted_keywords = extracted_keywords_data.get("technical_keywords", [])

        # Step 3: Get resume data for comparison
        logger.info(f"Getting resume data for user {application_data.user_id}")
        resume_data = {
            "skills": get_user_skills(db, application_data.user_id),
            "experiences": get_work_experience_descriptions(db, application_data.user_id),
            "projects": get_project_descriptions(db, application_data.user_id)
        }

        logger.info("Calculating matched and missing keywords.")
        keyword_match_result = calculate_matched_missing(
            extracted_keywords=extracted_keywords,
            resume_data=resume_data
        )
        
        # Step 5: Create and store analysis
        logger.info(f"Creating analysis data for application {application_response.id}")
        analysis_data = ApplicationAnalysisCreate(
            user_id=application_data.user_id,
            application_id=application_response.id,
            job_description=cleaned_description,
            extracted_keywords=json.dumps(extracted_keywords),
            matched_keywords=json.dumps(keyword_match_result.get('matched_keywords', [])),
            missing_keywords=json.dumps(keyword_match_result.get('missing_keywords', [])),
            relevant_experiences="",
            relevant_projects="",
            suggestions=json.dumps(suggestions)
        )

        # Store in database 
        logger.info(f"Storing analysis for application {application_response.id}")
        stored_analysis = application.store_application_analysis(
            db, analysis_data
        )

        logger.info("Fetching editor data for merging tailored resume.")
        editorData = application.get_editor_data_for_first_time(db, application_data.user_id)
        tailored_resume = merge_editor_data(tailored_resume, editorData)
        logger.info(f"Generating LaTeX file for tailored resume: {tailored_resume}")

        editor_content = json.dumps(tailored_resume)
        if not application.cached_resume_exists(db, application_data.user_id):
            logger.info("No cached resume. Creating one.")
            application.create_cached_resume(db, application_data.user_id, editor_content)
        else:
            logger.info("Cached resume found. Updating it.")
            application.update_editor_data(db, application_data.user_id, editor_content)

        return {
            "extracted_keywords": extracted_keywords,
            "matched_keywords": keyword_match_result.get('matched_keywords', []),
            "missing_keywords": keyword_match_result.get('missing_keywords', []),
            "suggestions": suggestions
        }

    except Exception as e:
        logger.error(f"Error in application analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing application: {str(e)}"
        )
