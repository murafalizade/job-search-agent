from job_search_agent.models.job_vacancy import JobVacancy
from abc import ABC, abstractmethod

class BaseSearchTool(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def search(self, query: str) -> str:
        pass

    @abstractmethod
    def normalize(self, raw_entry: dict) -> JobVacancy:
        pass