from pydantic import BaseModel

class JobVacancy(BaseModel):
    title: str
    company: str
    url: str
    source: str