from abc import ABC, abstractmethod

class BaseSearchTool(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def search(self, query: str) -> str:
        pass