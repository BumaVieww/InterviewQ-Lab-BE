from pydantic import BaseModel
from typing import Any, List, Generic, TypeVar

T = TypeVar('T')

class BaseResponse(BaseModel):
    message: str
    data: Any

class CursorPage(BaseModel, Generic[T]):
    values: List[T]
    has_next: bool