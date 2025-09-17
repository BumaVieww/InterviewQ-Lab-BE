from sqlalchemy.orm import Query
from typing import List, Optional, TypeVar, Generic
from api.schemas.base import CursorPage

T = TypeVar('T')

def paginate_cursor(
    query: Query,
    cursor_id: Optional[int] = None,
    size: int = 20,
    id_column = None
) -> CursorPage[T]:
    if cursor_id:
        query = query.filter(id_column > cursor_id)

    items = query.limit(size + 1).all()

    has_next = len(items) > size
    if has_next:
        items = items[:-1]

    return CursorPage(values=items, has_next=has_next)