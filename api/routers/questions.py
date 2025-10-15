from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, selectinload
from core.database import get_db
from core.auth import get_current_user
from core.pagination import paginate_cursor
from api.schemas.question import QuestionResponse, QuestionCreateRequest, QuestionUpdateRequest
from api.schemas.answer import AnswerResponse, AnswerCreateRequest
from api.schemas.base import BaseResponse, CursorPage
from app.domain.question.model.question import Question
from app.domain.question.model.answer import Answer
from app.domain.user.model.user import User
from app.domain.company.model.company import Company
from typing import Optional
import csv
import io
from datetime import date
import re

router = APIRouter(prefix="/questions", tags=["questions"])

def normalize_company_name(company_name: str) -> str:
    """회사명을 정규화합니다."""
    # 공백 제거 및 소문자 변환
    normalized = company_name.strip()

    # 주식회사, (주), 회사 등 불필요한 접미사 제거
    suffixes = ['주식회사', '(주)', '㈜', '회사', 'Inc', 'inc', 'Corp', 'corp', 'Co.', 'co.', 'Ltd', 'ltd', '(최종면접)', '(기술면접)', '(2차면접)', '(비대면면접)', 'ai 면접', '(컬쳐핏)', ]
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()

    # 특수문자 제거 (일부만)
    normalized = re.sub(r'[^\w가-힣\s]', '', normalized)

    return normalized.strip()

@router.post("/single", response_model=BaseResponse)
async def create_question(
    question_request: QuestionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    질문을 단건 등록합니다.
    """
    # 회사 존재 확인
    company = db.query(Company).filter(Company.company_id == question_request.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 질문 생성
    question = Question(
        registrant_id=current_user.user_id,
        company_id=question_request.company_id,
        question=question_request.question,
        category=question_request.category,
        tag=question_request.tag,
        question_at=date.today()
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return BaseResponse(message="질문 등록 성공", data=None)

@router.get("/sample-csv")
async def download_sample_csv():
    """
    질문 업로드를 위한 샘플 CSV 파일을 다운로드합니다.
    """
    from fastapi.responses import StreamingResponse
    
    # CSV 샘플 데이터
    sample_data = """company,question,category,question_at
삼성전자,자기소개를 해주세요.,인성면접,2024
네이버,프로젝트 경험을 말해주세요.,기술면접,2024
카카오,지원동기가 무엇인가요?,인성면접,2023"""
    
    # CSV 파일로 변환
    csv_bytes = sample_data.encode('utf-8-sig')  # BOM 추가로 엑셀에서 한글 깨짐 방지
    
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=question_upload_sample.csv"
        }
    )

@router.post("", response_model=BaseResponse)
@router.post("/", response_model=BaseResponse)
async def create_questions_from_csv(
    question: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    CSV 파일을 업로드하여 질문들을 bulk insert합니다.
    Admin만 접근 가능합니다.
    CSV 형식: company,question,category,question_at
    - question: 면접 질문, 꼬리 질문들이 많음
    - category: 지원 분야
    - company: 지원 회사명
    - question_at: 몇 학년도 데이터인지
    """
    # Admin 권한 체크
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # CSV 파일 검증
    if not question.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSV file required")

    try:
        # CSV 파일 읽기
        content = await question.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        questions_to_insert = []
        for row in csv_reader:
            # 필수 필드 검증
            if not all(key in row for key in ['company', 'question', 'category', 'question_at']):
                raise HTTPException(status_code=400, detail="CSV must contain: company, question, category, question_at")

            # 회사명 전처리
            normalized_company_name = normalize_company_name(row['company'])

            # 회사 조회 또는 생성
            company = db.query(Company).filter(Company.company_name == normalized_company_name).first()
            if not company:
                company = Company(company_name=normalized_company_name)
                db.add(company)
                db.flush()  # ID를 얻기 위해 flush

            # tag 자동 분류 (기본값: tenacity)
            tag = "technology" if "기술" in row['category'] or "개발" in row['category'] else "tenacity"

            question_obj = Question(
                registrant_id=current_user.user_id,
                company_id=company.company_id,
                question=row['question'],
                category=row['category'],
                tag=tag,
                question_at=row['question_at']
            )
            questions_to_insert.append(question_obj)

        # Bulk insert
        db.add_all(questions_to_insert)
        db.commit()

        return BaseResponse(message="질문 등록 성공.", data=None)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")

@router.get("", response_model=CursorPage[QuestionResponse])
@router.get("/", response_model=CursorPage[QuestionResponse])
async def get_questions(
    cursor_id: Optional[int] = None,
    size: int = 20,
    search: Optional[str] = None,
    company_name: Optional[str] = None,
    question_at: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    질문 목록을 조회합니다.
    
    - search: 질문 내용 전체 검색 (LIKE 검색)
    - company_name: 회사명으로 필터링 (부분 검색)
    - question_at: 학년도로 필터링 (예: 2024)
    """
    query = db.query(Question)
    
    # 전체 검색 - 질문 내용에서 검색
    if search:
        query = query.filter(Question.question.ilike(f"%{search}%"))
    
    # 회사명 필터 (부분 검색)
    if company_name:
        query = query.join(Company).filter(Company.company_name.ilike(f"%{company_name}%"))
    
    # 학년도 필터 (부분 검색)
    if question_at:
        query = query.filter(Question.question_at.ilike(f"%{question_at}%"))
    
    query = query.order_by(Question.question_id)
    return paginate_cursor(query, cursor_id, size, Question.question_id)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.patch("/{question_id}", response_model=BaseResponse)
async def update_question(
    question_id: int,
    question_request: QuestionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.registrant_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this question")

    question.question = question_request.question
    question.category = question_request.category
    question.tag = question_request.tag
    db.commit()
    return BaseResponse(message="Question updated successfully", data=None)

@router.delete("/{question_id}", response_model=BaseResponse)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.registrant_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this question")

    db.delete(question)
    db.commit()
    return BaseResponse(message="Question deleted successfully", data=None)

@router.post("/{question_id}/answers", response_model=BaseResponse)
async def create_answer(
    question_id: int,
    answer_request: AnswerCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db_answer = Answer(
        question_id=question_id,
        user_id=current_user.user_id,
        answer=answer_request.answer
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return BaseResponse(message="Answer created successfully", data=db_answer.answer_id)

@router.get("/{question_id}/answers", response_model=CursorPage[AnswerResponse])
async def get_question_answers(
    question_id: int,
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    query = db.query(Answer).filter(Answer.question_id == question_id).order_by(Answer.answer_id)
    return paginate_cursor(query, cursor_id, size, Answer.answer_id)