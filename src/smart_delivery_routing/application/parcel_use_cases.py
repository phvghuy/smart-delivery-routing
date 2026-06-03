import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from smart_delivery_routing.domain.linehaul import Parcel, ParcelQuery, ParcelRepository


@dataclass(frozen=True)
class ParcelNotFound(Exception):
    parcel_id: UUID

    def __str__(self) -> str:
        return f"Parcel '{self.parcel_id}' not found."


@dataclass(frozen=True)
class ParcelPage:
    items: list[Parcel]
    next_cursor: str | None


def _encode_cursor(item: Parcel) -> str:
    payload = {"created_at": item.created_at.isoformat(), "id": str(item.id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    return datetime.fromisoformat(payload["created_at"]), UUID(payload["id"])


def get_parcel(parcel_id: UUID, repo: ParcelRepository) -> Parcel:
    parcel = repo.get_by_id(parcel_id)
    if parcel is None:
        raise ParcelNotFound(parcel_id=parcel_id)
    return parcel


def list_parcels(
    query: ParcelQuery,
    repo: ParcelRepository,
    cursor: str | None = None,
) -> ParcelPage:
    if cursor is not None:
        cursor_created_at, cursor_id = _decode_cursor(cursor)
        query = ParcelQuery(
            page_size=query.page_size,
            statuses=query.statuses,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
        )
    rows = repo.list(query)
    has_next = len(rows) > query.page_size
    items = rows[:query.page_size]
    next_cursor = _encode_cursor(items[-1]) if has_next and items else None
    return ParcelPage(items=items, next_cursor=next_cursor)