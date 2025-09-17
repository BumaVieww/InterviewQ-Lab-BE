from pydantic import BaseModel

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
    company_id: int
    analysis_data: dict

    class Config:
        from_attributes = True