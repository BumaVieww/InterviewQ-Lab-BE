from pydantic import BaseModel
from datetime import date, datetime

class CompanyCreateRequest(BaseModel):
    company_name: str

class CompanyResponse(BaseModel):
    company_id: int
    company_name: str

    class Config:
        from_attributes = True

class PositionResponse(BaseModel):
    position_id: int
    position_name: str

    class Config:
        from_attributes = True

class CompanyAnalyzeResponse(BaseModel):
    company_analyze_id: int
    company_id: int
    result: str | None
    from_field: str | None
    analyzed_at: datetime | None
    
    class Config:
        from_attributes = True

class JobPostingResponse(BaseModel):
    company_job_posting_id: int
    company_id: int | None
    job_id: str | None
    overview: str | None
    key_responsibilities: str | None
    preferred_qualifications: str | None
    benefits_and_perks: str | None
    hiring_process: str | None
    employment_type: str | None
    application_deadline: date | None
    work_location: str | None
    
    class Config:
        from_attributes = True
