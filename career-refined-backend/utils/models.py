from pydantic import BaseModel
from typing import List
from typing import Optional

class WorkExperienceSchema(BaseModel):
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

class EducationSchema(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree_type: Optional[str] = None  # Bachelor's, Master's, PhD, etc.
    gpa: Optional[str] = None
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None

class ProjectSchema(BaseModel):
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

class UserSchema(BaseModel):
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
    work_experiences: Optional[List[WorkExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    projects: Optional[List[ProjectSchema]] = None