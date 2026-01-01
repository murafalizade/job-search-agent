from typing import List, Tuple
from job_search_agent.core.orchestration.graph import create_job_search_graph, AgentState, parse_cv_node, rank_jobs_node, optimize_job_node
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult
from job_search_agent.core.llm_gateways.gateway import get_gateway


class JobSearchOrchestrator:
    def __init__(self):
        self.graph = create_job_search_graph()
        self.gateway = get_gateway()
        
        self.state: AgentState = {
            "cv_text": None,
            "resume": None,
            "ranked_jobs": [],
            "selected_job_index": None,
            "optimization_result": None
        }

    async def process_cv(self, cv_text: str) -> Resume:
        """Parses CV into a structured Resume object."""
        self.state["cv_text"] = cv_text
        
        result = await parse_cv_node(self.state)
        self.state.update(result)
        
        return self.state["resume"]

    async def find_jobs(self) -> List[Tuple[JobVacancy, float]]:
        """Finds and ranks jobs based on the currently parsed resume."""
        if not self.state["resume"]:
            raise ValueError("No CV processed yet. Please upload a CV first.")
            
        result = await rank_jobs_node(self.state)
        self.state.update(result)
        
        return self.state["ranked_jobs"]

    async def optimize_job(self, job_index: int) -> OptimizationResult:
        """Optimizes a specific job using the LangGraph optimize_job node."""
        if not self.state["resume"]:
            raise ValueError("No CV processed yet. Please upload a CV first.")
        
        if job_index < 0 or job_index >= len(self.state["ranked_jobs"]):
            raise IndexError("Invalid job selection index.")
            
        self.state["selected_job_index"] = job_index

        result_state = await optimize_job_node(self.state)
        self.state.update(result_state)
        
        return self.state["optimization_result"]

    def get_usage_report(self) -> str:
        return self.gateway.cost_controller.get_report()