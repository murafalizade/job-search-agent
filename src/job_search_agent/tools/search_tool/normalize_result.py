from job_search_agent.models.job_vacancy import JobVacancy

def normalize_ddg(raw_entry: dict) -> JobVacancy:
    title = raw_entry.get("title", "Unknown").split("|")[0].strip()
    company = "Unknown"
    if "|" in raw_entry.get("title", ""):
        parts = raw_entry["title"].split("|")
        if len(parts) > 1:
            company = parts[1].strip()
    
    return JobVacancy(
        title=title,
        company=company,
        url=raw_entry.get("link"),
        source="DuckDuckGo"
    )
