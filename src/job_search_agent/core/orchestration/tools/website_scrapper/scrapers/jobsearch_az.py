from typing import Optional
import asyncio
import httpx
from bs4 import BeautifulSoup
import re

from job_search_agent.core.orchestration.tools.website_scrapper.base import BaseScraper
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class JobSearchAzScraper(BaseScraper):
    """Scraper implementation for jobsearch.az"""

    def can_handle(self, url: str) -> bool:
        return "jobsearch.az" in url

    async def scrape(self, url: str) -> Optional[JobVacancy]:
        # jobsearch.az modern site is client-side rendered (SPA).
        # We redirect to the classic subdomain which provides SSR content for the same IDs.
        if "classic.jobsearch.az" not in url and "jobsearch.az" in url:
            url = url.replace("jobsearch.az", "classic.jobsearch.az")

        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            html = response.text
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Title
        title_tag = soup.select_one("h1.vacancies__title, h1.vacancy__title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        if title == "N/A":
           return None
        
        # Company
        company = "N/A"
        company_tag = soup.select_one("h1.company__title, div.company__title h2, div.vacancies__provided span, div.vacancy__start")
        if company_tag:
            company = company_tag.get_text(strip=True)
        
        # Deadline
        deadline = "N/A"
        deadline_tag = soup.select_one("span.vacancy__dead-line, span.vacancy__deadline")
        if deadline_tag:
            deadline_text = deadline_tag.get_text(strip=True)
            # Remove labels like "Deadline" or "Son tarix"
            deadline = re.sub(r'(Deadline|Son tarix)', '', deadline_text, flags=re.IGNORECASE).strip()
        
        email = None
        email_span = soup.select_one("span.apply__send-mail")
        if email_span:
            email = email_span.get_text(strip=True)
        
        if not email:
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            if email_match:
                email = email_match.group(0)
        
        description_div = soup.select_one("div.vacancy__description.content, div.content-text, div#content_block.content")
        full_description = description_div.get_text("\n", strip=True).lstrip() if description_div else ""

        if not email and full_description:
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_description)
            if email_match:
                email = email_match.group(0)
        
        requirements = ""
        how_to_apply = ""
        salary = None
        if full_description:
            # Salary extraction
            salary_match = re.search(r'Əmək\s?haqqı[^\d]*([\d\s\+\-]+\s+\w+)', full_description, re.IGNORECASE)
            if salary_match:
                salary = salary_match.group(1).strip()
            
            # Section extraction
            req_keywords = [r"namizəd[ə\s]+(?:üçün\s+)?tələblər", r"tələblər", r"vəzifə\s+öhdəlikləri", r"requirements"]
            apply_keywords = [r"müraciət", r"cv\s+göndər", r"maraqlanan\s+namizədlər", r"how\s+to\s+apply"]
            
            all_patterns = req_keywords + apply_keywords
            combined_pattern = r'(' + '|'.join(all_patterns) + r')[:\s]*'
            
            matches = list(re.finditer(combined_pattern, full_description, re.IGNORECASE))
            
            for i, match in enumerate(matches):
                label = match.group(1).lower()
                start_content = match.end()
                next_start = matches[i+1].start() if i+1 < len(matches) else len(full_description)
                content = full_description[start_content:next_start].strip()
                
                # Check which group the label belongs to
                is_req = any(re.fullmatch(p, label, re.IGNORECASE) for p in req_keywords)
                is_apply = any(re.fullmatch(p, label, re.IGNORECASE) for p in apply_keywords)
                
                if is_req:
                    requirements = (requirements + "\n" + content).strip() if requirements else content
                elif is_apply:
                    # Keep the original label for context in how_to_apply
                    how_to_apply = (how_to_apply + "\n" + match.group(1) + " " + content).strip() if how_to_apply else (match.group(1) + " " + content)

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