from pydantic import BaseModel, Field
from typing import List
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.resume_models import Resume

class CVRequest(BaseModel):
    cv_text: str = Field(description="The full text content of the candidate's CV",
                         example="I am a software engineer with 5 years of experience in React and Python...")

class FindJobsRequest(BaseModel):
    resume: Resume = Field(description="The structured resume data")

class OptimizeJobRequest(BaseModel):
    resume: Resume = Field(description="The structured resume data")
    job: JobVacancy = Field(description="The job vacancy to optimize for")

class OptimizationRequest(BaseModel):
    job_index: int = Field(description='The index of the job from the ranked list to optimize for', example=0)

class JobResponse(BaseModel):
    job: JobVacancy
    score: float = Field(description="Matching score (0.0 to 1.0)", example=0.85)
    reason: str = Field(description="Explanation of why this job matches the resume", example="The candidate has relevant experience in Python and React.")

class ProcessCVResponse(BaseModel):
    resume: Resume

class FindJobsResponse(BaseModel):
    ranked_jobs: List[JobResponse]
