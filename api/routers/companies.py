from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.pagination import paginate_cursor
from api.schemas.company import CompanyCreateRequest, CompanyResponse, CompanyAnalyzeResponse, PositionResponse, JobPostingResponse
from api.schemas.base import BaseResponse, CursorPage
from app.domain.company.model.company import Company
from app.domain.company.model.position import Position
from app.domain.company.model.company_job_posting import CompanyJobPosting
from app.domain.company.model.company_analyze import CompanyAnalyze
from typing import Optional

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("", response_model=CursorPage[CompanyResponse])
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

@router.post("", response_model=BaseResponse)
@router.post("/", response_model=BaseResponse)
async def create_company(
    company_request: CompanyCreateRequest,
    db: Session = Depends(get_db)
):
    """
    회사를 생성합니다.
    """
    # 중복 회사명 검사
    existing_company = db.query(Company).filter(
        Company.company_name == company_request.company_name
    ).first()

    if existing_company:
        raise HTTPException(status_code=400, detail="Company with this name already exists")

    # 회사 생성
    company = Company(company_name=company_request.company_name)
    db.add(company)
    db.commit()
    db.refresh(company)

    return BaseResponse(message="Company created successfully", data=company.company_id)

@router.get("/analyze", response_model=CursorPage[CompanyAnalyzeResponse])
async def get_company_analyses(
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """
    회사 분석(Company Analyze) 목록을 조회합니다.
    
    - cursor_id: 커서 기반 페이지네이션을 위한 마지막 company_analyze_id
    - size: 페이지 크기 (기본값: 20)
    """
    query = db.query(CompanyAnalyze).order_by(CompanyAnalyze.company_analyze_id)
    return paginate_cursor(query, cursor_id, size, CompanyAnalyze.company_analyze_id)

@router.get("/analyze/{analyze_id}", response_model=CompanyAnalyzeResponse)
async def get_company_analyze(analyze_id: int, db: Session = Depends(get_db)):
    """
    특정 회사 분석(Company Analyze)을 단건 조회합니다.
    
    - analyze_id: 분석 ID (company_analyze_id)
    """
    analyze = db.query(CompanyAnalyze).filter(
        CompanyAnalyze.company_analyze_id == analyze_id
    ).first()
    if not analyze:
        raise HTTPException(status_code=404, detail="Company analyze not found")
    return analyze

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

@router.get("/{company_id}/analyze", response_model=CursorPage[CompanyAnalyzeResponse])
async def get_company_analyses_by_company(
    company_id: int,
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """
    특정 회사의 분석(Company Analyze) 목록을 조회합니다.
    
    - company_id: 회사 ID
    - cursor_id: 커서 기반 페이지네이션을 위한 마지막 company_analyze_id
    - size: 페이지 크기 (기본값: 20)
    """
    # 회사 존재 확인
    company = db.query(Company).filter(Company.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    query = db.query(CompanyAnalyze).filter(
        CompanyAnalyze.company_id == company_id
    ).order_by(CompanyAnalyze.company_analyze_id)
    
    return paginate_cursor(query, cursor_id, size, CompanyAnalyze.company_analyze_id)
