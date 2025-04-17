from pydantic import BaseModel
from typing import List
from typing import Optional
from app.models.education import EducationModel
from app.models.project import ProjectModel
from app.models.work_experience import WorkExperienceModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

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

class SkillModel(BaseModel):
    skills: str

class LanguageModel(BaseModel):
    languages: str

class CertificationModel(BaseModel):
    certifications: str

class PersonalInfoModel(BaseModel):
    name: str
    email: str
    phone_number: str


class PersonalDetailsUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    portfolio_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None

class ResumeDataModel(BaseModel):
    class Education(BaseModel):
        institution: str
        degree: str
        startYear: str
        endYear: str

    class Experience(BaseModel):
        company: str
        role: str
        startDate: str
        endDate: Optional[str] = None
        location: Optional[str] = None
        responsibilities: List[str]

    class PersonalDetails(BaseModel):
        name: str
        phone: str
        email: str
        github: str
        linkedin: str

    class Project(BaseModel):
        name: str
        technologies: str
        startDate: str
        endDate: Optional[str] = None
        description: List[str]

    class Skills(BaseModel):
        languages: Optional[str] = None
        frameworks: Optional[str] = None
        developerTools: Optional[str] = None
        cloudTechnologies: Optional[str] = None
        dbsApplications: Optional[str] = None
        otherSkillsAndTools: Optional[str] = None

    education: List[Education]
    experience: List[Experience]
    personalDetails: PersonalDetails
    projects: List[Project]
    skills: Skills

class MessageOut(BaseModel):
    message: str