from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    user_id: int
    nickname: str
    email: str
    role: str
    is_onboarding: bool

    class Config:
        from_attributes = True

class UserCreateRequest(BaseModel):
    nickname: str
    email: str

class UserUpdateRequest(BaseModel):
    nickname: str

class UserPositionUpdateRequest(BaseModel):
    position_ids: list[int]
    company_ids: list[int]