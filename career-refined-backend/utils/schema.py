from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    resume = Column(String, nullable=True)  # Path to the uploaded file
    
    portfolio_link = Column(String, nullable=True)
    linkedin_link = Column(String, nullable=True)
    github_link = Column(String, nullable=True)

    skills = Column(Text, nullable=True)  # Store as a comma-separated list
    languages = Column(Text, nullable=True)  # Store as a comma-separated list
    certifications = Column(Text, nullable=True)  # Store as a comma-separated list

    work_experiences = relationship("WorkExperience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class WorkExperience(Base):
    __tablename__ = "work_experience"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    position = Column(String, nullable=False)
    experience_type = Column(String, nullable=False)  # Full-time, Part-time, Internship
    start_month = Column(String, nullable=False)
    start_year = Column(Integer, nullable=False)
    end_month = Column(String, nullable=True)
    end_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    currently_work_here = Column(Boolean, default=False)

    user = relationship("User", back_populates="work_experiences")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    school_name = Column(String, nullable=False)
    major = Column(String, nullable=True)
    degree_type = Column(String, nullable=True)  # Bachelor's, Master's, PhD, etc.
    gpa = Column(String, nullable=True)
    start_month = Column(String, nullable=False)
    start_year = Column(Integer, nullable=False)
    end_month = Column(String, nullable=True)
    end_year = Column(Integer, nullable=True)

    user = relationship("User", back_populates="education")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    project_name = Column(String, nullable=False)
    company = Column(String, nullable=True)  # Optional, if done in a company
    location = Column(String, nullable=True)
    position = Column(String, nullable=True)
    experience_type = Column(String, nullable=True)  # Personal, Academic, Work-related
    start_month = Column(String, nullable=False)
    start_year = Column(Integer, nullable=False)
    end_month = Column(String, nullable=True)
    end_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    project_link = Column(String, nullable=True)

    user = relationship("User", back_populates="projects")
