import logging
from fastapi import APIRouter, HTTPException, status, Depends
from job_search_agent.api.models import CVRequest, SearchResponse, JobResponse, OptimizationRequest
from job_search_agent.api.dependencies import get_orchestrator
from job_search_agent.core.orchestration.orchestrator import JobSearchOrchestrator
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/core", tags=["Core"])

@router.post("/process-cv", 
             response_model=SearchResponse, 
             status_code=status.HTTP_200_OK,
             summary="Parse CV and find matching jobs")
async def process_cv(
    request: CVRequest, 
    orchestrator: JobSearchOrchestrator = Depends(get_orchestrator)
):
    """
    Takes raw CV text, parses it into structured data, and searches for matching job vacancies 
    across local job boards using multilingual embeddings.
    """
    try:
        logger.info("Processing new CV upload...")
        resume, ranked_jobs = orchestrator.process_cv(request.cv_text)
        
        formatted_jobs = [
            JobResponse(job=job, score=score) 
            for job, score in ranked_jobs
        ]
        
        return SearchResponse(
            resume=resume,
            ranked_jobs=formatted_jobs
        )
    except Exception as e:
        logger.error(f"Error processing CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to process CV: {str(e)}"
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
        result = orchestrator.optimize_job(request.job_index)
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
