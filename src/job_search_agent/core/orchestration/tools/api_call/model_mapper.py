def map_glorri_response(response: dict) -> str:
    company = response.get("company") or {}

    return f"https://jobs.glorri.com/vacancies/{company.get("slug", "")}/{response.get('slug', '')}"
