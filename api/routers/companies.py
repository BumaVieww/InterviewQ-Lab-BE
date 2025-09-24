from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.pagination import paginate_cursor
from api.schemas.company import CompanyResponse, CompanyAnalyzeResponse
from api.schemas.base import BaseResponse, CursorPage
from app.domain.company.model.company import Company
from typing import Optional

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=CursorPage[CompanyResponse])
async def get_companies(
    cursor_id: Optional[int] = None,
    size: int = 20,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Company)

    if name:
        query = query.filter(Company.company_name.ilike(f"%{name}%"))

    query = query.order_by(Company.company_id)
    return paginate_cursor(query, cursor_id, size, Company.company_id)

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.delete("/{company_id}", response_model=BaseResponse)
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()
    return BaseResponse(message="Company deleted successfully", data=None)

@router.get("/analyze/{company_id}", response_model=CompanyAnalyzeResponse)
async def get_company_analysis(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # TODO: Implement actual company analysis logic
    analysis_data = {
        "total_questions": 0,
        "popular_categories": [],
        "trending_tags": [],
        "analysis_summary": "Company analysis not yet implemented"
    }

    return CompanyAnalyzeResponse(
        company_id=company_id,
        analysis_data=analysis_data
    )