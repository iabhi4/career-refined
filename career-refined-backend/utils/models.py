from pydantic import BaseModel, EmailStr, validator
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
    technologies_used: Optional[str] = None
    @validator('experience_type')
    def validate_experience_type(cls, v):
        valid_types = ['Full-time', 'Part-time', 'Internship']
        if v not in valid_types:
            raise ValueError(f'experience_type must be one of {valid_types}')
        return v
    
    @validator('start_month')
    def validate_start_month(cls, v):
        valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        if v not in valid_months:
            raise ValueError(f'start_month must be one of {valid_months}')
        return v

    @validator('end_month')
    def validate_end_month(cls, v):
        if v is not None:
            valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            if v not in valid_months:
                raise ValueError(f'end_month must be one of {valid_months}')
        return v

    @validator('end_year')
    def validate_year_range(cls, v, values):
        if v is not None:
            if 'start_year' in values and v < values['start_year']:
                raise ValueError('end_year cannot be before start_year')
        return v


class EducationModel(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree_type: Optional[str] = None  # Bachelor's, Master's, PhD, etc.
    gpa: Optional[str] = None
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None
    @validator('degree_type')
    def validate_degree_type(cls, v):
        if v is not None:
            valid_types = ["Bachelor's", "Master's", "PhD", "Associate's", "High School", "Other"]
            if v not in valid_types:
                raise ValueError(f'degree_type must be one of {valid_types}')
        return v
    
    @validator('start_month')
    def validate_start_month(cls, v):
        valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        if v not in valid_months:
            raise ValueError(f'start_month must be one of {valid_months}')
        return v

    @validator('end_month')
    def validate_end_month(cls, v):
        if v is not None:
            valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            if v not in valid_months:
                raise ValueError(f'end_month must be one of {valid_months}')
        return v

    @validator('end_year')
    def validate_year_range(cls, v, values):
        if v is not None:
            if 'start_year' in values and v < values['start_year']:
                raise ValueError('end_year cannot be before start_year')
        return v

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
    technologies_used: Optional[str] = None
    @validator('experience_type')
    def validate_experience_type(cls, v):
        if v is not None:
            valid_types = ['Personal', 'Academic', 'Work-related']
            if v not in valid_types:
                raise ValueError(f'experience_type must be one of {valid_types}')
        return v
    
    @validator('start_month')
    def validate_start_month(cls, v):
        valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        if v not in valid_months:
            raise ValueError(f'start_month must be one of {valid_months}')
        return v

    @validator('end_month')
    def validate_end_month(cls, v):
        if v is not None:
            valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            if v not in valid_months:
                raise ValueError(f'end_month must be one of {valid_months}')
        return v

    @validator('end_year')
    def validate_year_range(cls, v, values):
        if v is not None:
            if 'start_year' in values and v < values['start_year']:
                raise ValueError('end_year cannot be before start_year')
        return v

class UserModel(BaseModel):
    name: str
    email: str
    phone_number: Optional[str] = None
    location: Optional[str] = None
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
    id: Optional[int] = None
    user_id: int
    job_role: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: str
    date_applied: Optional[datetime] = None
    application_status: Optional[str] = "Draft"

class Token(BaseModel):
    user_id: int
    is_onboarded: bool

class TokenData(BaseModel):
    email: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    is_onboarded: bool
    class Config:
        from_attributes = True