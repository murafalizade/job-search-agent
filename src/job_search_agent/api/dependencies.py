from functools import lru_cache
from job_search_agent.core.orchestration.orchestrator import JobSearchOrchestrator

@lru_cache
def get_orchestrator() -> JobSearchOrchestrator:
    """Returns a singleton instance of the JobSearchOrchestrator."""
    return JobSearchOrchestrator()
