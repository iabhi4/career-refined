from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base

class Auth(Base):
    __tablename__ = "auth"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_onboarded = Column(Boolean, default=False)
    
    # One-to-one relationship with User
    user = relationship("User", back_populates="auth_info", uselist=False)