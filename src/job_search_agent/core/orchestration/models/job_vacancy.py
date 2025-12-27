from typing import Optional
from pydantic import BaseModel

class JobVacancy(BaseModel):
    title: str
    company: str
    deadline: str
    url: str
    source: str
    description: str
    requirements: str
    how_to_apply: str
    salary: Optional[str]
    email: Optional[str]