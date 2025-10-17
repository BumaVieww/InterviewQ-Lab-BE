from charset_normalizer import from_bytes
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import case
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
from app.domain.user.model.user_position import UserPosition
from app.domain.user.model.goal_company import GoalCompany
from app.domain.company.model.position import Position
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
        question_at=date(date.today().year, 1, 1)  # 년도의 1월 1일로 저장
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

    # 파일 형식 검증
    filename = question.filename.lower()
    if not filename.endswith('.csv') and not filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="CSV or XLSX file required")

    try:
        content = await question.read()
        
        # 파일 형식에 따라 처리
        if filename.endswith('.xlsx'):
            # XLSX 파일 처리
            import openpyxl
            workbook = openpyxl.load_workbook(io.BytesIO(content))
            sheet = workbook.active
            
            # 헤더 추출 (첫 번째 행)
            headers = [cell.value for cell in sheet[1]]
            
            # 데이터 행을 딕셔너리로 변환
            rows = []
            for row_cells in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = dict(zip(headers, row_cells))
                rows.append(row_dict)
        else:
            # CSV 파일 읽기 (한글 지원)
            encoding = from_bytes(content).best().encoding or "utf-8"
            csv_content = content.decode(encoding, errors="replace")
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)
        
        questions_to_insert = []
        for row in rows:
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
                question_at=date(int(row['question_at']), 1, 1)  # 년도를 Date로 변환
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    질문 목록을 조회합니다.

    - search: 질문 내용 전체 검색 (LIKE 검색)
    - company_name: 회사명으로 필터링 (부분 검색)
    - question_at: 학년도로 필터링 (예: 2024)

    우선순위 정렬:
    - Goal Company 매칭: +2점 (사용자가 등록한 목표 회사)
    - User Position 매칭: +1점 (질문 category에 사용자의 직무명 포함)
    - 점수 내림차순 → question_id 내림차순
    """

    # 사용자의 goal_company 목록 조회 (list로 변환)
    user_goal_company_ids = [
        gc.company_id for gc in db.query(GoalCompany).filter(
            GoalCompany.user_id == current_user.user_id
        ).all()
    ]

    # 사용자의 position 이름 조회
    user_positions = db.query(Position.position_name).join(
        UserPosition, UserPosition.position_id == Position.position_id
    ).filter(
        UserPosition.user_id == current_user.user_id
    ).all()

    # position 이름 리스트 생성
    position_names = [pos.position_name for pos in user_positions if pos.position_name]

    # 우선순위 점수 계산
    # Goal Company 매칭: +2점
    goal_company_score = case(
        (Question.company_id.in_(user_goal_company_ids), 2) if user_goal_company_ids else (False, 0),
        else_=0
    )

    # User Position 매칭: +1점
    if position_names:
        # category에 position_name이 포함되어 있으면 점수 부여
        conditions = [Question.category.ilike(f"%{name}%") for name in position_names]
        position_score = case(
            *[(condition, 1) for condition in conditions],
            else_=0
        )
    else:
        position_score = 0

    # 총 우선순위 점수
    priority_score = goal_company_score + position_score

    # 쿼리 구성
    query = db.query(Question)

    # 전체 검색 - 질문 내용에서 검색
    if search:
        query = query.filter(Question.question.ilike(f"%{search}%"))

    # 회사명 필터 (부분 검색)
    if company_name:
        query = query.join(Company).filter(Company.company_name.ilike(f"%{company_name}%"))

    # 학년도 필터 (부분 검색)
    if question_at:
        from sqlalchemy import cast, String
        query = query.filter(cast(Question.question_at, String).ilike(f"%{question_at}%"))

    # 우선순위 점수를 추가하여 조회
    query = query.add_columns(priority_score.label('priority'))

    # 우선순위 점수 내림차순 → question_id 내림차순 정렬
    query = query.order_by(priority_score.desc(), Question.question_id.desc())

    # 커서 페이지네이션 적용
    # NOTE: 우선순위 정렬과 커서 페이지네이션을 함께 사용할 때의 제한사항:
    # - question_id < cursor_id 필터링은 우선순위가 다른 항목들 간 순서를 보장하지 않음
    # - 완벽한 페이지네이션을 위해서는 모든 데이터를 메모리에 로드하거나
    # - offset 기반 페이지네이션 사용, 또는 복합 커서 (priority, id) 사용 필요
    # TODO: 데이터가 많아지면 offset 기반으로 변경 고려
    if cursor_id is not None:
        query = query.filter(Question.question_id < cursor_id)

    # size + 1개 가져와서 has_next 판단
    questions_with_priority = query.limit(size + 1).all()
    questions = [q[0] for q in questions_with_priority]

    # has_next 판단
    has_next = len(questions) > size
    values = questions[:size]

    # CursorPage 응답 생성
    return CursorPage(values=values, has_next=has_next)

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

    if not current_user.role == "admin":
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