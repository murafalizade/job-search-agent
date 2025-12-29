from pydantic import BaseModel, Field

class OptimizationResult(BaseModel):
    explanation: str = Field(description="Detailed explanation of how the candidate's profile matches the job requirements")
    optimization_tips: str = Field(description="Actionable tips to improve the CV for this specific job")
    cover_letter: str = Field(description="A professional cover letter tailored to the job and the candidate's experience")