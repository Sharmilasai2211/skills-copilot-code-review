"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _parse_ymd(date_value: str, field_name: str) -> datetime:
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be in YYYY-MM-DD format"
        ) from error


def _require_signed_in_user(username: Optional[str]) -> Dict[str, Any]:
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required for this action")

    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _serialize_announcement(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "message": document["message"],
        "start_date": document.get("start_date"),
        "expiration_date": document["expiration_date"]
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_announcements(include_expired: bool = False) -> List[Dict[str, Any]]:
    """Get announcements. By default returns only active (not expired) entries."""
    query: Dict[str, Any] = {}

    if not include_expired:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        query = {
            "expiration_date": {"$gte": today},
            "$or": [
                {"start_date": None},
                {"start_date": {"$exists": False}},
                {"start_date": {"$lte": today}}
            ]
        }

    announcements = [
        _serialize_announcement(announcement)
        for announcement in announcements_collection.find(query).sort("expiration_date", 1)
    ]
    return announcements


@router.post("", response_model=Dict[str, Any])
def create_announcement(
    message: str,
    expiration_date: str,
    teacher_username: Optional[str] = Query(None),
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new announcement. Requires signed-in teacher."""
    _require_signed_in_user(teacher_username)

    cleaned_message = message.strip()
    if not cleaned_message:
        raise HTTPException(status_code=400, detail="message is required")

    parsed_expiration = _parse_ymd(expiration_date, "expiration_date")
    parsed_start = _parse_ymd(start_date, "start_date") if start_date else None

    if parsed_start and parsed_start > parsed_expiration:
        raise HTTPException(status_code=400, detail="start_date cannot be after expiration_date")

    announcement_id = cleaned_message.lower().replace(" ", "-")[:42]
    announcement_id = f"{announcement_id}-{int(datetime.now(timezone.utc).timestamp())}"

    document = {
        "_id": announcement_id,
        "message": cleaned_message,
        "start_date": start_date,
        "expiration_date": expiration_date
    }
    announcements_collection.insert_one(document)

    return _serialize_announcement(document)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    message: str,
    expiration_date: str,
    teacher_username: Optional[str] = Query(None),
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing announcement. Requires signed-in teacher."""
    _require_signed_in_user(teacher_username)

    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")

    cleaned_message = message.strip()
    if not cleaned_message:
        raise HTTPException(status_code=400, detail="message is required")

    parsed_expiration = _parse_ymd(expiration_date, "expiration_date")
    parsed_start = _parse_ymd(start_date, "start_date") if start_date else None

    if parsed_start and parsed_start > parsed_expiration:
        raise HTTPException(status_code=400, detail="start_date cannot be after expiration_date")

    update_payload = {
        "message": cleaned_message,
        "start_date": start_date,
        "expiration_date": expiration_date
    }

    announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": update_payload}
    )

    return _serialize_announcement({"_id": announcement_id, **update_payload})


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None)
) -> Dict[str, str]:
    """Delete an announcement. Requires signed-in teacher."""
    _require_signed_in_user(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
