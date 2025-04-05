from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class CachedResume(Base):
    __tablename__ = "cached_resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    editor_content = Column(Text, nullable=False)
    pdf_url = Column(String, nullable=False)

    user = relationship("User", back_populates="cached_resumes") 