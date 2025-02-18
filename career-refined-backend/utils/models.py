from pydantic import BaseModel, EmailStr
from typing import List
from typing import Optional
from datetime import datetime

class WorkExperienceModel(BaseModel):
    company: str
    location: Optional[str] = None
    position: str
    experience_type: str  # Full-time, Part-time, Internship
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None
    description: Optional[str] = None
    currently_work_here: bool

class EducationModel(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree_type: Optional[str] = None  # Bachelor's, Master's, PhD, etc.
    gpa: Optional[str] = None
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None

class ProjectModel(BaseModel):
    project_name: str
    company: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    experience_type: Optional[str] = None  # Personal, Academic, Work-related
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None
    description: Optional[str] = None
    project_link: Optional[str] = None

class UserModel(BaseModel):
    name: str
    email: str
    phone_number: Optional[str] = None
    location: Optional[str] = None
    resume: Optional[str] = None  # Path to the uploaded file
    portfolio_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    work_experiences: Optional[List[WorkExperienceModel]] = None
    education: Optional[List[EducationModel]] = None
    projects: Optional[List[ProjectModel]] = None

class JobDescriptionRequest(BaseModel):
    job_description: str

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: int
    auth_id: int

class ApplicationAnalysisCreate(BaseModel):
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
    id: int
    user_id: int
    job_role: str
    company: str
    location: str
    job_description: str
    date_applied: datetime
    application_status: str
