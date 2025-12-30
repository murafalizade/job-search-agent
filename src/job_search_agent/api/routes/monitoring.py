from fastapi import APIRouter, Depends
from job_search_agent.api.dependencies import get_orchestrator
from job_search_agent.core.orchestration.orchestrator import JobSearchOrchestrator

router = APIRouter(tags=["Monitoring"])

@router.get("/", tags=["General"], summary="Health check")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "version": "1.1.0",
        "message": "Job Search Agent API is ready to process requests."
    }

@router.get("/usage", summary="Get usage and cost report")
async def get_usage(orchestrator: JobSearchOrchestrator = Depends(get_orchestrator)):
    """
    Returns a detailed report of LLM token usage and estimated costs in USD.
    """
    return {
        "report": orchestrator.get_usage_report(),
        "currency": "USD"
    }
