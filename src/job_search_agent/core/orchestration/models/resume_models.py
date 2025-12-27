from pydantic import BaseModel, Field
from typing import List

class Resume(BaseModel):
    titles: List[str] = Field(description="Array of job titles held or targeted")
    skills: List[str] = Field(description="Array of technical and soft skills")
    seniority: str = Field(description="Seniority level (e.g., Junior, Mid, Senior, Lead)")
    years_experience: int = Field(description="Total years of professional experience")
    preferred_locations: List[str] = Field(description="List of preferred work locations or remote preferences")
    keywords: List[str] = Field(description="Important keywords extracted from the CV for job matching")
