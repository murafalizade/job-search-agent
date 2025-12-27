import json
from urllib.parse import urlparse
from langchain_community.tools import DuckDuckGoSearchResults

from job_search_agent.core.orchestration.tools.search_tool.base import BaseSearchTool
from job_search_agent.core.orchestration.tools.search_tool.trusted_websites import TRUSTED_WEBSITES, is_from_trusted_domain



class DuckDuckGoSearchTool(BaseSearchTool):
    def __init__(self, max_results: int = 10):
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
        urls = []
        
        for website in TRUSTED_WEBSITES:            
            web_results_json = self.client.run(f"site:{website} {query}")
                    
            web_results = json.loads(web_results_json)
                    
            for entry in web_results:
                url = entry.get("link", "")
                        
                if not is_from_trusted_domain(url):
                    print(f"Filtered out: {url} (not from {website})")
                    continue
                        
                url = entry.get("link", "")
                if url in urls:
                    print(f"Dublicated link: {url}")
                    break
                urls.append(url)
                            
        return urls

if __name__ == "__main__":
    tool = DuckDuckGoSearchTool(max_results=10)
    vacancies = tool.search("frontend developer")    
    print(f"\n\nTotal vacancies found: {len(vacancies)}")    
    print("\n" + "="*70)
    print("SERIALIZED JSON:")
    print("="*70)
    print(vacancies)