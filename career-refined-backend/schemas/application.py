from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from config.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to users table
    job_role = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    job_description = Column(Text, nullable=True)
    date_applied = Column(TIMESTAMP, default=None)  # Will default to CURRENT_TIMESTAMP
    extracted_job_keywords = Column(Text, nullable=True)  # Store as comma-separated list or JSON
    final_resume_used = Column(String, nullable=True)
    application_status = Column(String, default="Pending")  # Default status is 'Pending'
    add_to_tracker = Column(Boolean, default=False)

    user = relationship("User", back_populates="applications")
    application_analysis = relationship("ApplicationAnalysis", back_populates="application", uselist=False)