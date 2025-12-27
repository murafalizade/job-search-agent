from urllib.parse import urlparse

TRUSTED_WEBSITES = [
    "jobsearch.az",
    # "jobs.glorri.com"
]

def is_from_trusted_domain(url: str) -> bool:
    """
        Check if URL is from the trusted domain
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
            
        domain = domain.replace('www.', '')

        for website in TRUSTED_WEBSITES:
            if website in domain:
                return True
            
        return False
    
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return False