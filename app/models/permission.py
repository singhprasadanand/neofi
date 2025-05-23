from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.utils.db_utils.database import Base

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    role = Column(String, nullable=False)

    user = relationship("User", back_populates="permissions")
    event = relationship("Event", back_populates="permissions")