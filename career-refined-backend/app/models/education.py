from pydantic import BaseModel, validator
from typing import Optional

class EducationModel(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree_type: Optional[str] = None  # Bachelor's, Master's, PhD, etc.
    gpa: Optional[str] = None
    start_month: str
    start_year: int
    end_month: Optional[str] = None
    end_year: Optional[int] = None
    @validator('degree_type')
    def validate_degree_type(cls, v):
        if v is not None:
            valid_types = ["Bachelor's", "Master's", "PhD", "Associate's", "High School", "Other"]
            if v not in valid_types:
                raise ValueError(f'degree_type must be one of {valid_types}')
        return v
    
    @validator('start_month')
    def validate_start_month(cls, v):
        valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if v not in valid_months:
            raise ValueError(f'start_month must be one of {valid_months}')
        return v

    @validator('end_month')
    def validate_end_month(cls, v):
        if v is not None:
            valid_months = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            if v not in valid_months:
                raise ValueError(f'end_month must be one of {valid_months}')
        return v

    @validator('end_year')
    def validate_year_range(cls, v, values):
        if v is not None:
            if 'start_year' in values and v < values['start_year']:
                raise ValueError('end_year cannot be before start_year')
        return v