from typing import TypedDict, List, Tuple, Optional
from langgraph.graph import StateGraph, END

from job_search_agent.core.orchestration.agents.resume_agent import ResumeAgent
from job_search_agent.core.orchestration.agents.resume_ranking_agent import ResumeRankingAgent
from job_search_agent.core.orchestration.agents.job_optimizer_agent import JobOptimizerAgent
from job_search_agent.core.orchestration.models.resume_models import Resume
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy
from job_search_agent.core.orchestration.models.optimization_result import OptimizationResult

class AgentState(TypedDict):
    """The state of the job search agent."""
    cv_text: Optional[str]
    resume: Optional[Resume]
    ranked_jobs: List[Tuple[JobVacancy, float]]
    selected_job_index: Optional[int]
    optimization_result: Optional[OptimizationResult]

async def parse_cv_node(state: AgentState):
    """Parses the CV text into a structured Resume object."""
    agent = ResumeAgent()
    resume = await agent.parse_cv(state["cv_text"])
    return {"resume": resume}

async def rank_jobs_node(state: AgentState):
    """Searches and ranks jobs based on the parsed Resume."""
    agent = ResumeRankingAgent()
    ranked_jobs = await agent.run(state["resume"])
    return {"ranked_jobs": ranked_jobs}

async def optimize_job_node(state: AgentState):
    """Optimizes a specific job application."""
    agent = JobOptimizerAgent()
    job_index = state["selected_job_index"]
    
    if job_index is None or job_index < 0 or job_index >= len(state["ranked_jobs"]):
        raise ValueError("Invalid job index for optimization.")
        
    selected_job = state["ranked_jobs"][job_index][0]
    result = await agent.run(job=selected_job, resume=state["resume"])
    return {"optimization_result": result}

def create_job_search_graph():
    """Creates the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_cv", parse_cv_node)
    workflow.add_node("rank_jobs", rank_jobs_node)
    workflow.add_node("optimize_job", optimize_job_node)

    workflow.set_entry_point("parse_cv")
    workflow.add_edge("parse_cv", "rank_jobs")
    workflow.add_edge("rank_jobs", END)
    
    return workflow.compile()
