from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobDescriptionRequest(BaseModel):
    job_description: str

class ApplicationAnalysisCreate(BaseModel):
    user_id: int
    application_id: int
    job_description: str
    extracted_keywords: str
    matched_keywords: str
    missing_keywords: str
    relevant_experiences: str
    relevant_projects: str
    suggestions: str

class ApplicationAnalysisResponse(BaseModel):
    id: int
    missing_keywords: str
    matched_keywords: str
    relevant_experiences: str
    relevant_projects: str
    suggestions: str

class ApplicationModel(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    job_role: str
    company: str
    location: str
    job_description: str
    date_applied: Optional[datetime] = None
    application_status: Optional[str] = "Draft"
    add_to_tracker: Optional[bool] = False

class EditorModel(BaseModel):
    editor_content: str
