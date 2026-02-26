"""
Announcement endpoints for the High School Management System API
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementPayload(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    expires_at: str
    starts_at: Optional[str] = None


def _parse_date(value: str, field_name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be in YYYY-MM-DD format"
        )


def _require_signed_in_user(teacher_username: Optional[str]) -> None:
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")


def _serialize_announcement(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "message": doc.get("message", ""),
        "starts_at": doc.get("starts_at"),
        "expires_at": doc.get("expires_at"),
        "created_at": doc.get("created_at")
    }


def _build_id_query(announcement_id: str) -> Dict[str, Any]:
    query_options: List[Dict[str, Any]] = [{"_id": announcement_id}]
    if ObjectId.is_valid(announcement_id):
        query_options.append({"_id": ObjectId(announcement_id)})
    return {"$or": query_options}


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements for the banner."""
    today = date.today().isoformat()
    query = {
        "expires_at": {"$gte": today},
        "$or": [
            {"starts_at": None},
            {"starts_at": {"$exists": False}},
            {"starts_at": {"$lte": today}},
        ]
    }

    announcements = []
    for announcement in announcements_collection.find(query).sort("expires_at", 1):
        announcements.append(_serialize_announcement(announcement))

    return announcements


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(
    teacher_username: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    """Get all announcements for announcement management."""
    _require_signed_in_user(teacher_username)

    announcements = []
    for announcement in announcements_collection.find({}).sort("created_at", -1):
        announcements.append(_serialize_announcement(announcement))

    return announcements


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def create_announcement(
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Create an announcement. Requires authentication."""
    _require_signed_in_user(teacher_username)

    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    expires_at = _parse_date(payload.expires_at, "expires_at")
    starts_at = _parse_date(payload.starts_at, "starts_at") if payload.starts_at else None

    if starts_at and expires_at < starts_at:
        raise HTTPException(
            status_code=400,
            detail="expires_at must be the same as or after starts_at"
        )

    document = {
        "_id": str(uuid4()),
        "message": payload.message.strip(),
        "starts_at": starts_at.isoformat() if starts_at else None,
        "expires_at": expires_at.isoformat(),
        "created_at": date.today().isoformat(),
    }

    result = announcements_collection.insert_one(document)
    created = announcements_collection.find_one({"_id": result.inserted_id})
    return _serialize_announcement(created)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementPayload,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an announcement. Requires authentication."""
    _require_signed_in_user(teacher_username)

    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    expires_at = _parse_date(payload.expires_at, "expires_at")
    starts_at = _parse_date(payload.starts_at, "starts_at") if payload.starts_at else None

    if starts_at and expires_at < starts_at:
        raise HTTPException(
            status_code=400,
            detail="expires_at must be the same as or after starts_at"
        )

    result = announcements_collection.update_one(
        _build_id_query(announcement_id),
        {
            "$set": {
                "message": payload.message.strip(),
                "starts_at": starts_at.isoformat() if starts_at else None,
                "expires_at": expires_at.isoformat(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    announcement = announcements_collection.find_one(_build_id_query(announcement_id))
    return _serialize_announcement(announcement)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, str]:
    """Delete an announcement. Requires authentication."""
    _require_signed_in_user(teacher_username)

    result = announcements_collection.delete_one(_build_id_query(announcement_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
