from typing import Optional
import httpx
from bs4 import BeautifulSoup
import re

from job_search_agent.core.orchestration.tools.website_scrapper.base import BaseScraper
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class GlorriScraper(BaseScraper):
    """Scraper implementation for glorri.com"""

    def can_handle(self, url: str) -> bool:
        return "glorri.com" in url

    async def scrape(self, url: str) -> Optional[JobVacancy]:
        async with httpx.AsyncClient() as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            try:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                html = response.text
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Title - usually in h1
        title_tag = soup.select_one("h1")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        
        # Company
        company_tag = soup.select_one("a[href*='/company/'], .company-name")
        company = company_tag.get_text(strip=True) if company_tag else "N/A"

        # Description and Requirements based on provided HTML
        description = ""
        requirements = ""
        
        # Find all h3 tags and their following description-html divs
        h3_tags = soup.find_all("h3", class_=lambda x: x and "text-semibold" in x)
        for h3 in h3_tags:
            header_text = h3.get_text(strip=True).lower()
            # Find the next div with class description-html
            content_div = h3.find_next("div", class_="description-html")
            if content_div:
                content = content_div.get_text("\n", strip=True)
                if "təsvir" in header_text or "öhdəlik" in header_text:
                    description = content
                elif "tələblər" in header_text:
                    requirements = content

        # Sidebar info
        deadline = "N/A"
        experience = "N/A"
        education = "N/A"
        job_type = "N/A"
        category = "N/A"
        
        sidebar_items = soup.select("div.flex.justify-between")
        for item in sidebar_items:
            label_tag = item.select_one("p.text-neutral-80")
            value_tag = item.select_one("p.font-semibold")
            if label_tag and value_tag:
                label = label_tag.get_text(strip=True).lower()
                value = value_tag.get_text(strip=True)
                if "son tarix" in label:
                    deadline = value
                elif "təcrübə" in label:
                    experience = value
                elif "təhsil" in label:
                    education = value
                elif "vakansiya növü" in label:
                    job_type = value

        category_tag = soup.select_one("span.text-accent-yellow")
        if category_tag:
            category = category_tag.get_text(strip=True)

        # Prepend extra info to requirements for better matching
        extra_info = []
        if experience != "N/A": extra_info.append(f"Təcrübə: {experience}")
        if education != "N/A": extra_info.append(f"Təhsil: {education}")
        if job_type != "N/A": extra_info.append(f"Növ: {job_type}")
        if category != "N/A": extra_info.append(f"Kateqoriya: {category}")
        
        if extra_info:
            requirements = "\n".join(extra_info) + "\n\n" + (requirements or "")

        # Email extraction
        email = None
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        if email_match:
            email = email_match.group(0)

        return JobVacancy(
            title=title,
            company=company,
            deadline=deadline,
            url=url,
            source="glorri.com",
            description=description or "See website",
            requirements=requirements or "See website",
            how_to_apply="Apply via Glorri",
            salary=None,
            email=email
        )