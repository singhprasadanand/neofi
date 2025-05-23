from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.events import EventUpdate, EventCreate, EventOut, PermissionOut, PermissionShare, PermissionUpdate, \
    VersionOut
from app.models.user import User
from app.utils.db_utils.database import get_db
from app.services.user import get_current_user
from app.utils.role_config import get_user_role, can_view, can_edit, can_delete, can_share
from app.services import events

events_router = APIRouter()


@events_router.post("/", response_model=EventOut, status_code=201)
def create_event(
        event_in: EventCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return events.create_event(db=db, user=current_user, event_in=event_in)


@events_router.get("/", response_model=list[EventOut])
def list_events(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return events.list_events(db=db, user=current_user)


@events_router.get("/{event_id}", response_model=EventOut)
def get_event(
        event_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_view(role):
        raise HTTPException(status_code=403, detail="Permission denied")

    return event


@events_router.put("/{event_id}", response_model=EventOut)
def update_event(
        event_id: int,
        event_in: EventUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_edit(role):
        raise HTTPException(status_code=403, detail="Permission denied")

    return events.update_event(db, event_id, event_in)


@events_router.delete("/{event_id}", status_code=204)
def delete_event(
        event_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_delete(role):
        raise HTTPException(status_code=403, detail="Permission denied")

    events.delete_event(db, event_id)
    return {"message": "event deleted successfully"}


@events_router.post("/batch", response_model=list[EventOut])
def create_events_batch(
        events_in: list[EventCreate],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return events.create_events_batch(db=db, user=current_user, events_in=events_in)


@events_router.post('/{event_id}/share', response_model=list[PermissionOut])
def share_permission(
        event_id: int,
        event_share: list[PermissionShare],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_share(role):
        raise HTTPException(status_code=403, detail="Permission denied")

    return events.share_permission(db=db, event_id=event_id, event_share=event_share)


@events_router.get('/{event_id}/permissions', response_model=list[PermissionOut])
def list_all_permissions(
        event_id: int,
        db: Session = Depends(get_db),
):
    return events.get_event_permissions(db=db, event_id=event_id)


@events_router.put('/{event_id}/permissions/{user_id}', response_model=PermissionOut)
def update_permission(
        event_id: int,
        user_id: int,
        update: PermissionUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_share(role):
        raise HTTPException(status_code=403, detail="Permission denied")

    updated = events.update_user_permission(db=db, event_id=event_id,
                                            user_id=user_id, update=update)
    if not updated:
        raise HTTPException(status_code=404, detail="Permission not found")
    return updated


@events_router.delete("{event_id}/permissions/{user_id}", status_code=204)
def delete_permission(event_id: int,
                      user_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)
                      ):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_delete(role):
        raise HTTPException(status_code=403, detail="Permission denied")
    deleted = events.delete_user_permission(db, event_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": f"Permission deleted for User: {user_id}"}


@events_router.get("/{event_id}/history/{version_id}", response_model=VersionOut)
def get_version(event_id: int,
                version_id: int,
                db: Session = Depends(get_db)
                ):
    version = events.get_event_version(db, event_id, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@events_router.post("/{event_id}/rollback/{version_id}", response_model=EventOut)
def rollback_version(event_id: int,
                     version_id: int,
                     db: Session = Depends(get_db)
                     ):
    rolled_back_event = events.rollback_event_version(db, event_id, version_id)
    if not rolled_back_event:
        raise HTTPException(status_code=404, detail="Version or event not found")
    return rolled_back_event


@events_router.get("/{event_id}/changelog", response_model=list[VersionOut])
def get_event_changelog(
        event_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    event = events.get_event_by_id(db, event_id)
    role = get_user_role(current_user.id, event)
    if not can_view(role):
        raise HTTPException(status_code=403, detail="Permission denied")
    versions = events.get_all_event_versions(db=db, event_id=event_id)
    if not versions:
        raise HTTPException(status_code=404, detail="No changelog found")
    return versions


@events_router.get("/{event_id}/diff/{version_id1}/{version_id2}")
def get_event_diff(
        event_id: int,
        version_id1: int,
        version_id2: int,
        db: Session = Depends(get_db)
):
    v1 = events.get_event_version(db=db, event_id=event_id, version_id=version_id1)
    v2 = events.get_event_version(db=db, event_id=event_id, version_id=version_id2)
    if not v1 or not v2:
        raise HTTPException(status_code=404, detail="One or both versions not found")

    diff = dict()
    for column in v1.__table__.columns:
        diff[column.name] = {'version_1': getattr(v1, column.name), 'version_2': getattr(v2, column.name)}

    return {"diff": diff}
