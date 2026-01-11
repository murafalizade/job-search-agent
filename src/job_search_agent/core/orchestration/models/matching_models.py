from pydantic import BaseModel, Field
from typing import List, Dict

class BatchJobMatchResult(BaseModel):
    matching_indices: List[int] = Field(description="List of indices of jobs that are a good match (0-indexed based on the input list)")
    reasons: Dict[int, str] = Field(description="A dictionary mapping the job index to a brief reason for the match/mismatch decision")