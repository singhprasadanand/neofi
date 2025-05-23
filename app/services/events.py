import datetime

from sqlalchemy.orm import Session

from app.schemas.events import EventCreate, EventUpdate, EventOut, PermissionShare, PermissionUpdate
from app.models.events import Event, EventVersion
from app.models.permission import Permission
from app.models.user import User


def create_event(db: Session, user: User, event_in: EventCreate):
    event = Event(**event_in.dict(), owner_id=user.id)
    db.add(event)
    db.commit()
    db.refresh(event)

    permission = Permission(user_id=user.id, event_id=event.id, role="owner")
    db.add(permission)
    db.commit()

    version = EventVersion(
        event_id=event.id,
        version_number=1,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        is_recurring=event.is_recurring,
        recurrence_pattern=event.recurrence_pattern,
        owner_id=event.owner_id,
        created_at=datetime.datetime.now()
    )
    db.add(version)
    db.commit()

    return event


def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


def list_events(db: Session, user: User):
    return (
        db.query(Event)
        .join(Permission)
        .filter_by(user_id=user.id)
        .all()
    )


def update_event(db: Session, event_id: int, event_in: EventUpdate):
    event = get_event_by_id(db, event_id)
    for key, value in event_in.dict(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)

    latest_version_number = db.query(EventVersion).filter_by(event_id=event.id).count() + 1
    version = EventVersion(
        event_id=event.id,
        version_number=latest_version_number,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        is_recurring=event.is_recurring,
        recurrence_pattern=event.recurrence_pattern,
        owner_id=event.owner_id,
        created_at=datetime.datetime.now()
    )
    db.add(version)
    db.commit()

    return event


def delete_event(db: Session, event_id: int):
    event = get_event_by_id(db, event_id)
    if not event:
        return

    db.query(EventVersion).filter_by(event_id=event_id).delete()

    db.query(Permission).filter_by(event_id=event_id).delete()

    db.delete(event)
    db.commit()


def create_events_batch(db: Session, user: User, events_in: list[EventCreate]):
    events = []
    for event_in in events_in:
        event = create_event(db, user, event_in)
        events.append(event)
    return events


def share_permission(db: Session, event_id: int, event_share: list[PermissionShare]):
    for user in event_share:
        print(user.role)
        perm = db.query(Permission).filter_by(event_id=event_id, user_id=user.user_id).first()
        if perm:
            perm.role = user.role.value
        else:
            perm = Permission(event_id=event_id, user_id=user.user_id, role=user.role.value)
            db.add(perm)
    db.commit()
    return db.query(Permission).filter_by(event_id=event_id).all()


def get_event_permissions(db: Session, event_id: int):
    return db.query(Permission).filter_by(event_id=event_id).all()


def update_user_permission(db: Session, event_id: int, user_id: int, update: PermissionUpdate):
    permission = db.query(Permission).filter_by(event_id=event_id, user_id=user_id).first()
    if not permission:
        return None
    permission.role = update.role
    db.commit()
    db.refresh(permission)
    return permission


def delete_user_permission(db: Session, event_id: int, user_id: int):
    permission = db.query(Permission).filter_by(event_id=event_id, user_id=user_id).first()
    if not permission:
        return False
    db.delete(permission)
    db.commit()
    return True


def get_event_version(db: Session, event_id: int, version_id: int):
    return db.query(EventVersion).filter_by(event_id=event_id, id=version_id).first()


def rollback_event_version(db: Session, event_id: int, version_id: int):
    version = get_event_version(db, event_id, version_id)
    if not version:
        return None

    event = get_event_by_id(db, event_id)



    # Apply rollback
    event.title = version.title
    event.description = version.description
    event.start_time = version.start_time
    event.end_time = version.end_time
    event.location = version.location
    event.is_recurring = version.is_recurring
    event.recurrence_pattern = version.recurrence_pattern

    db.commit()
    db.refresh(event)
    return event


def get_all_event_versions(db: Session, event_id: int):
    return db.query(EventVersion).filter_by(event_id=event_id).order_by(EventVersion.version_number.asc()).all()
