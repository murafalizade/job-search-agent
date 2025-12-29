from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Tuple
from job_search_agent.core.orchestration.orchestrator import JobSearchOrchestrator
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult

app = FastAPI(
    title="Job Search Agent API",
    description="API for parsing CVs, searching jobs, and optimizing applications.",
    version="1.0.0"
)

# Singleton orchestrator
orchestrator = JobSearchOrchestrator()

class CVRequest(BaseModel):
    cv_text: str

class OptimizationRequest(BaseModel):
    job_index: int

class JobResponse(BaseModel):
    job: JobVacancy
    score: float

class SearchResponse(BaseModel):
    resume: Resume
    ranked_jobs: List[JobResponse]

@app.get("/")
async def root():
    return {"message": "Job Search Agent API is running"}

@app.post("/process-cv", response_model=SearchResponse)
async def process_cv(request: CVRequest):
    """
    Upload CV text to parse it and find matching jobs.
    """
    try:
        resume, ranked_jobs = orchestrator.process_cv(request.cv_text)
        
        # Format response
        formatted_jobs = [
            JobResponse(job=job, score=score) 
            for job, score in ranked_jobs
        ]
        
        return SearchResponse(
            resume=resume,
            ranked_jobs=formatted_jobs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-job", response_model=OptimizationResult)
async def optimize_job(request: OptimizationRequest):
    """
    Optimize the application for a specific job chosen from the previous search.
    """
    try:
        result = orchestrator.optimize_job(request.job_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IndexError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usage")
async def get_usage():
    """
    Get the current cost and token usage report.
    """
    return {"report": orchestrator.get_usage_report()}
