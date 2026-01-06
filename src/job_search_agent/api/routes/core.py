import logging
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from job_search_agent.api.models import CVRequest, ProcessCVResponse, JobResponse, OptimizationRequest, FindJobsResponse
from job_search_agent.api.dependencies import get_orchestrator
from job_search_agent.core.orchestration.orchestrator import JobSearchOrchestrator
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/core", tags=["Core"])

@router.post("/process-cv", 
             response_model=ProcessCVResponse, 
             status_code=status.HTTP_200_OK,
             summary="Parse CV into structured data")
async def process_cv(
    file: UploadFile,
    orchestrator: JobSearchOrchestrator = Depends(get_orchestrator)
):
    """
    Takes raw CV text and parses it into structured data (Resume object).
    """
    try:
        logger.info("Parsing CV...")
        if file.content_type != "text/plain":
            pdf_bytes = await file.read()
            resume = await orchestrator.process_cv(pdf_bytes)
            return ProcessCVResponse(resume=resume)
        else:
            raise ValueError("Invalid file type. Please upload a PDF file.")
    except Exception as e:
        logger.error(f"Error parsing CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to parse CV: {str(e)}"
        )

@router.post("/find-jobs", 
             response_model=FindJobsResponse, 
             status_code=status.HTTP_200_OK,
             summary="Find matching jobs based on processed CV")
async def find_jobs(
    orchestrator: JobSearchOrchestrator = Depends(get_orchestrator)
):
    """
    Searches for matching job vacancies across local job boards using the currently parsed Resume.
    Requires /process-cv to have been called first.
    """
    try:
        logger.info("Searching for matching jobs...")
        ranked_jobs = await orchestrator.find_jobs()
        
        formatted_jobs = [
            JobResponse(job=job, score=score) 
            for job, score in ranked_jobs
        ]
        
        return FindJobsResponse(ranked_jobs=formatted_jobs)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to find jobs: {str(e)}"
        )

@router.post("/optimize-job", 
             response_model=OptimizationResult, 
             summary="Optimize application for a specific job")
async def optimize_job(
    request: OptimizationRequest,
    orchestrator: JobSearchOrchestrator = Depends(get_orchestrator)
):
    """
    Generates a tailored cover letter and specific CV optimization tips for a previously 
    found job vacancy. Requires a CV to have been processed first.
    """
    try:
        logger.info(f"Optimizing for job index: {request.job_index}")
        result = await orchestrator.optimize_job(request.job_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Job index not found in recent search results."
        )
    except Exception as e:
        logger.error(f"Error optimizing job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
