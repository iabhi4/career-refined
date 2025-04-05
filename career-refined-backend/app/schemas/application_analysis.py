from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ApplicationAnalysis(Base):
    __tablename__ = "application_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_description = Column(Text)
    extracted_keywords = Column(Text)  # Store as JSON string
    matched_keywords = Column(Text)    # Store as JSON string
    missing_keywords = Column(Text)    # Store as JSON string
    relevant_experiences = Column(Text) # Store as JSON string
    relevant_projects = Column(Text)    # Store as JSON string
    suggestions = Column(Text)          # Store as JSON string
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    application = relationship("Application", back_populates="application_analysis")
    user = relationship("User", back_populates="application_analysis")