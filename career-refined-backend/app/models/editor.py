# app/schemas/editor.py (REVISED - example name StrictEditorDataSchema)

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

# Define nested models with ONLY the required fields
class StrictExperienceSchema(BaseModel):
    company: Optional[str] = None # Allow null if LLM can't find it
    role: Optional[str] = None
    responsibilities: Optional[str] = None

class StrictProjectSchema(BaseModel):
    name: Optional[str] = None
    technologies: Optional[str] = None
    description: Optional[str] = None

class SkillsSchema(BaseModel): # Keep this definition as before
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    developerTools: List[str] = Field(default_factory=list)
    cloudTechnologies: List[str] = Field(default_factory=list)
    dbsApplications: List[str] = Field(default_factory=list)
    otherSkillsAndTools: List[str] = Field(default_factory=list)

    # # Optional validator to remove empty skill categories before final output
    # @validator('*', pre=True, each_item=False) # <--- Pydantic V1 Decorator Syntax
    # def remove_empty_lists(cls, v, field):     # <--- Uses 'field', invalid in V2
    #     # ... implementation attempt ...
    #     pass # Keep empty lists for now, prompt asks LLM not to include them
    #     return v


# Schema for extracted keywords part
class ExtractedKeywordsSchema(BaseModel):
    technical_keywords: List[str] = Field(default_factory=list)



# Define the main EditorData schema matching the new prompt's Instruction 8
# Rename it or replace your existing EditorDataSchema
class StrictEditorDataSchema(BaseModel):
    experience: List[StrictExperienceSchema] = Field(default_factory=list)
    projects: List[StrictProjectSchema] = Field(default_factory=list)
    # Make skills non-optional if it should always be present, otherwise Optional
    skills: SkillsSchema = Field(default_factory=SkillsSchema)

    # NOTE: personalDetails and education are intentionally REMOVED from this schema

class CombinedRagOutputSchema(BaseModel):
    tailored_resume: StrictEditorDataSchema = Field(default_factory=StrictEditorDataSchema)
    extracted_keywords: ExtractedKeywordsSchema = Field(default_factory=ExtractedKeywordsSchema)
    # NEW: Replace 'suggestions' with 'improvement_feedback' list
    improvement_feedback: List[str] = Field(default_factory=list)
