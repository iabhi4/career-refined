from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

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
    technologies_used = Column(Text, nullable=True)  # Store as a comma-separated list
    project_link = Column(String, nullable=True)

    user = relationship("User", back_populates="projects")