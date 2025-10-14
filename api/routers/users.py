from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from core.database import get_db
from core.auth import get_current_user
from core.pagination import paginate_cursor
from api.schemas.user import UserResponse, UserCreateRequest, UserUpdateRequest, UserPositionUpdateRequest
from api.schemas.company import PositionResponse, CompanyResponse
from api.schemas.base import BaseResponse, CursorPage
from app.domain.user.model.user import User
from app.domain.company.model.position import Position
from app.domain.company.model.company import Company
from app.domain.user.model.user_position import UserPosition
from app.domain.user.model.goal_company import GoalCompany
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=UserResponse)
@router.get("/", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("", response_model=BaseResponse)
@router.post("/", response_model=BaseResponse)
async def create_user(user_request: UserCreateRequest, current_user: User = Depends(get_current_user)):
    # 이미 get_current_user에서 사용자가 생성되므로 여기서는 업데이트만 수행
    return BaseResponse(message="User already exists or created", data=current_user.user_id)

@router.patch("", response_model=BaseResponse)
@router.patch("/", response_model=BaseResponse)
async def update_user(
    user_request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.nickname = user_request.nickname
    db.commit()
    return BaseResponse(message="User updated successfully", data=None)

@router.get("/positions", response_model=CursorPage[PositionResponse])
async def get_all_positions(
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Position).order_by(Position.position_id)
    return paginate_cursor(query, cursor_id, size, Position.position_id)

@router.patch("/positions", response_model=BaseResponse)
async def update_user_goals(
    request: UserPositionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete existing user positions and goal companies
    db.query(UserPosition).filter(UserPosition.user_id == current_user.user_id).delete()
    db.query(GoalCompany).filter(GoalCompany.user_id == current_user.user_id).delete()

    # Add new positions
    for position_id in request.position_ids:
        user_position = UserPosition(user_id=current_user.user_id, position_id=position_id)
        db.add(user_position)

    # Add new goal companies
    for company_id in request.company_ids:
        goal_company = GoalCompany(user_id=current_user.user_id, company_id=company_id)
        db.add(goal_company)

    db.commit()
    return BaseResponse(message="User goals updated successfully", data=None)

@router.get("/positions/my", response_model=CursorPage[PositionResponse])
async def get_user_positions(
    cursor_id: Optional[int] = None,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = (db.query(Position)
             .join(UserPosition)
             .filter(UserPosition.user_id == current_user.user_id)
             .order_by(Position.position_id))
    return paginate_cursor(query, cursor_id, size, Position.position_id)

@router.get("/companies/my", response_model=CursorPage[CompanyResponse])
async def get_user_goal_companies(
    cursor_id: Optional[int] = None,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = (db.query(Company)
             .join(GoalCompany)
             .filter(GoalCompany.user_id == current_user.user_id)
             .order_by(Company.company_id))
    return paginate_cursor(query, cursor_id, size, Company.company_id)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user