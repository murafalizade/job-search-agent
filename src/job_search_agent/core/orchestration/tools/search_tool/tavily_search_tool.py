import concurrent.futures
import threading
from tavily import TavilyClient
from job_search_agent.core.orchestration.tools.search_tool.base import BaseSearchTool
from job_search_agent.core.orchestration.tools.search_tool.trusted_websites import TRUSTED_WEBSITES, is_from_trusted_domain
from job_search_agent.configs.setting import get_settings
from job_search_agent.core.orchestration.models.job_vacancy import JobVacancy

class TavilySearchTool(BaseSearchTool):
    def __init__(self, max_results: int = 20):
        settings = get_settings()
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY.get_secret_value())
        self.max_results = max_results
        self._lock = threading.Lock()

    def search(self, query: str) -> list[str]:
        """
        Search across trusted websites using Tavily and return list of unique links.
        Thread-safe parallel execution for multiple websites.
        """
        all_unique_urls = set()
        
        def search_single_website(website: str) -> list[str]:
            try:
                search_query = f"site:{website} {query.lower()}"
                # Using Tavily search API
                response = self.client.search(
                    query=search_query,
                    max_results=self.max_results,
                    search_depth="advanced"
                )
                
                valid_urls = []
                for result in response.get("results", []):
                    url = result.get("url")
                    if url and is_from_trusted_domain(url):
                        valid_urls.append(url)
                return valid_urls
            except Exception as e:
                print(f"Error searching {website} with Tavily: {e}")
                return []

        # Parallel execution across trusted websites
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_site = {
                executor.submit(search_single_website, site): site 
                for site in TRUSTED_WEBSITES
            }
            
            for future in concurrent.futures.as_completed(future_to_site):
                site_urls = future.result()
                
                # Thread-safe update of the unique URLs set
                with self._lock:
                    for url in site_urls:
                        if url not in all_unique_urls:
                            all_unique_urls.add(url)
                            print(f"Tavily added link: {url}")
                        else:
                            print(f"Tavily skipped duplicate link: {url}")
                            
        return list(all_unique_urls)

    def scrape(self, url: str) -> str:
        """
        Scrape a URL using Tavily's extract API.
        """
        try:
            response = self.client.extract(urls=[url])
            results = response.get("results", [])
            if results:
                return results[0].get("raw_content", "")
            return ""
        except Exception as e:
            print(f"Error scraping with Tavily: {e}")
            return ""
