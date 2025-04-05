from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Text, Date, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(Integer, ForeignKey("auth.id"), unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
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
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    auth_info = relationship("Auth", back_populates="user")
    application_analysis = relationship("ApplicationAnalysis", back_populates="user")
    cached_resumes = relationship("CachedResume", back_populates="user", cascade="all, delete-orphan")