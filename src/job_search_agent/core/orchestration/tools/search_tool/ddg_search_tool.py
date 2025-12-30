import json
from urllib.parse import urlparse
from langchain_community.tools import DuckDuckGoSearchResults

from job_search_agent.core.orchestration.tools.search_tool.base import BaseSearchTool
from job_search_agent.core.orchestration.tools.search_tool.trusted_websites import TRUSTED_WEBSITES, is_from_trusted_domain



class DuckDuckGoSearchTool(BaseSearchTool):
    def __init__(self, max_results: int = 20):
        self.client = DuckDuckGoSearchResults(
            num_results=max_results, 
            output_format='json', 
            utf8=True
        )
    
    def search(self, query: str) -> list[str]:
        """
        Search across trusted websites for job vacancies and return list of links
        
        Args:
            query: Search query (e.g., "frontend developer")
        """
        import concurrent.futures
        
        def search_website(website: str) -> list[str]:
            try:
                web_results_json = self.client.run(f"site:{website} {query}")
                web_results = json.loads(web_results_json)
                
                site_urls = []
                for entry in web_results:
                    url = entry.get("link", "")
                    if url and is_from_trusted_domain(url):
                        site_urls.append(url)
                return site_urls
            except Exception as e:
                print(f"Error searching {website}: {e}")
                return []

        all_urls = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_site = {executor.submit(search_website, site): site for site in TRUSTED_WEBSITES}
            for future in concurrent.futures.as_completed(future_to_site):
                site_urls = future.result()
                for url in site_urls:
                    if url not in all_urls:
                        all_urls.append(url)
                        print(f"Added link: {url}")
                    else:
                        print(f"Dublicated link: {url}")
                            
        return all_urls