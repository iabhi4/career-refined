from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from config.database import Base

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
    technologies_used = Column(Text, nullable=True)  # Store as a comma-separated list
    currently_work_here = Column(Boolean, default=False)

    user = relationship("User", back_populates="work_experiences")