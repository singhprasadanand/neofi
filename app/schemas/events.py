from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import RoleEnum


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class PermissionSchema(BaseModel):
    user_id: int
    role: RoleEnum

    class Config:
        orm_mode = True


class EventOut(EventBase):
    id: int
    owner_id: int
    permissions: list[PermissionSchema] | PermissionSchema = None

    class Config:
        orm_mode = True


class PermissionOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    role: RoleEnum


class PermissionShare(BaseModel):
    user_id: int
    role: RoleEnum


class PermissionUpdate(BaseModel):
    role: RoleEnum


class VersionOut(BaseModel):
    id: int
    event_id: int
    version_number: int
    title: str
    created_at: datetime
