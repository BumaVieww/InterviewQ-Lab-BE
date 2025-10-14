from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.pagination import paginate_cursor
from api.schemas.company import CompanyResponse, CompanyAnalyzeResponse, PositionResponse, JobPostingResponse
from api.schemas.base import BaseResponse, CursorPage
from app.domain.company.model.company import Company
from app.domain.company.model.position import Position
from app.domain.company.model.company_job_posting import CompanyJobPosting
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


@router.get("/job-postings", response_model=CursorPage[JobPostingResponse])
async def get_job_postings(
    cursor_id: Optional[int] = None,
    size: int = 20,
    company_name: Optional[str] = None,
    employment_type: Optional[str] = None,
    work_location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    채용공고(Job Posting) 목록을 조회합니다.
    
    - cursor_id: 커서 기반 페이지네이션을 위한 마지막 company_job_posting_id
    - size: 페이지 크기 (기본값: 20)
    - company_name: 회사명으로 필터링 (부분 검색)
    - employment_type: 고용 형태로 필터링
    - work_location: 근무 지역으로 필터링
    """
    query = db.query(CompanyJobPosting)

    # 회사명으로 필터링 (조인 필요)
    if company_name:
        query = query.join(Company).filter(Company.company_name.ilike(f"%{company_name}%"))
    
    # 고용 형태로 필터링
    if employment_type:
        query = query.filter(CompanyJobPosting.employment_type.ilike(f"%{employment_type}%"))
    
    # 근무 지역으로 필터링
    if work_location:
        query = query.filter(CompanyJobPosting.work_location.ilike(f"%{work_location}%"))

    query = query.order_by(CompanyJobPosting.company_job_posting_id)
    return paginate_cursor(query, cursor_id, size, CompanyJobPosting.company_job_posting_id)

@router.get("/job-postings/{job_posting_id}", response_model=JobPostingResponse)
async def get_job_posting(job_posting_id: int, db: Session = Depends(get_db)):
    """
    특정 채용공고(Job Posting)를 조회합니다.
    """
    job_posting = db.query(CompanyJobPosting).filter(
        CompanyJobPosting.company_job_posting_id == job_posting_id
    ).first()
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job_posting
