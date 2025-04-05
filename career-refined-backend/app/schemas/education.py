from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

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
    #location = Column(String, nullable=True)

    user = relationship("User", back_populates="education")