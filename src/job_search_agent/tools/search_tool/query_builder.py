from job_search_agent.models.resume_models import ResumeData

def build_query(resume: ResumeData) -> str:
    primary_role = resume.titles[0]
    return f"{primary_role}"
