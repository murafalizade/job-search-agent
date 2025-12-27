import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re
from job_search_agent.core.orchestration.tools.website_scrapper.base import BaseScraper
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class JobSearchAzScraper(BaseScraper):
    """Scraper implementation for jobsearch.az"""

    def can_handle(self, url: str) -> bool:
        return "jobsearch.az" in url

    async def scrape(self, url: str) -> JobVacancy:
        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            html = response.text
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Title
        title_tag = soup.find("h1", class_="vacancies__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        
        # Company
        company = "N/A"
        company_div = soup.find("div", class_="company__title")
        if company_div and company_div.find("h2"):
            company = company_div.find("h2").get_text(strip=True)
        else:
            provided_div = soup.find("div", class_="vacancies__provided")
            if provided_div and provided_div.find("span"):
                company = provided_div.find("span").get_text(strip=True)
        
        # Deadline
        deadline = "N/A"
        deadline_span = soup.find("span", class_="vacancy__dead-line")
        if deadline_span:
            deadline_text = deadline_span.get_text(strip=True)
            deadline = deadline_text.replace("Deadline", "").strip()
        
        # Email
        email = None
        email_span = soup.find("span", class_="apply__send-mail")
        if email_span:
            email = email_span.get_text(strip=True)
        
        # Description and Requirements extraction
        description_div = soup.find("div", class_="vacancy__description content")
        full_description = description_div.get_text("\n", strip=True) if description_div else ""
        
        requirements = ""
        how_to_apply = ""
        salary = None
        
        if description_div:
            # Attempt to split sections
            content_html = str(description_div)
            
            # Salary extraction from text
            salary_match = re.search(r'Əmək haqqı[:\s]*([\d\s\+]+AZN[^\.]*)', full_description, re.IGNORECASE)
            if salary_match:
                salary = salary_match.group(1).strip()
            
            # Requirements section usually starts after "Namizəd üçün tələblər"
            parts = re.split(r'(Namizəd üçün tələblər:|İş şəraiti:|Maraqlanan namizədlər)', full_description, flags=re.IGNORECASE)
            
            for i, part in enumerate(parts):
                lowered_part = part.lower()
                if "namizəd üçün tələblər" in lowered_part:
                    if i + 1 < len(parts):
                        requirements = parts[i+1].strip()
                elif "maraqlanan namizədlər" in lowered_part:
                    if i + 1 < len(parts):
                        how_to_apply = part + " " + parts[i+1].strip()

        # Fallback for how_to_apply
        if not how_to_apply:
            apply_info = soup.find("div", class_="apply-info")
            if apply_info:
                how_to_apply = apply_info.get_text(strip=True)
                if email:
                    how_to_apply += f" Email: {email}"

        return JobVacancy(
            title=title,
            company=company,
            deadline=deadline,
            url=url,
            source="jobsearch.az",
            description=full_description,
            requirements=requirements or "See description",
            how_to_apply=how_to_apply or "Apply via email",
            salary=salary,
            email=email
        )

if __name__ == '__main__':  
    print(JobSearchAzScraper().scrape('https://jobsearch.az/vacancies/123456'))
