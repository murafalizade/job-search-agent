import json
from langchain_community.tools import DuckDuckGoSearchResults
from job_search_agent.tools.search_tool.base import BaseSearchTool
from job_search_agent.tools.search_tool.trusted_websites import TRUSTED_WEBSITES
from job_search_agent.models.job_vacancy import JobVacancy

class DuckDuckGoSearchTool(BaseSearchTool):
    def __init__(self, max_results: int = 3):
        self.client = DuckDuckGoSearchResults(num_results=max_results, output_format='json', utf8=True)

    def normalize(self, raw_entry: str) -> JobVacancy:
        parsed = {}
        for part in raw_entry.split(": "):
            if ": " in part:
                key, value = part.split(": ", 1)
                parsed[key.strip()] = value.strip()

        title_raw = parsed.get("title", "Unknown")
        title = title_raw.split("|")[0].strip()

        company = "Unknown"
        if "|" in title_raw:
            parts = title_raw.split("|")
            if len(parts) > 1:
                company = parts[1].strip()

        url = parsed.get("link", "")

        return JobVacancy(
            title=title,
            company=company,
            url=url,
            source="DuckDuckGo"
        )

    def search(self, query: str) -> list[dict]:
        results = []
        for website in TRUSTED_WEBSITES:
            query = f"site:{website} frontend developer"
            web_results = self.client.run(query)
            print(web_results)
        
            results.append(self.normalize(web_results))
        
        return results
    


if __name__ == "__main__":
    tool = DuckDuckGoSearchTool()
    print(tool.search("frontend developer"))