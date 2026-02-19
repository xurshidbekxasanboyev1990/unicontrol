"""
UniControl - Room Model
========================
Room/Auditorium management for the university.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config import TASHKENT_TZ
from app.database import Base


class Room(Base):
    """
    Room/Auditorium model.
    
    Manages university rooms, their capacity, type and equipment.
    """
    
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Room info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Room name/number (e.g., 401-xona)"
    )
    building: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Building name (e.g., A bino)"
    )
    floor: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Floor number"
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
        comment="Seating capacity"
    )
    
    # Room type
    room_type: Mapped[str] = mapped_column(
        String(50),
        default="lecture",
        nullable=False,
        comment="Room type: lecture, lab, computer, conference, gym, other"
    )
    
    # Equipment
    has_projector: Mapped[bool] = mapped_column(Boolean, default=False)
    has_computer: Mapped[bool] = mapped_column(Boolean, default=False)
    has_whiteboard: Mapped[bool] = mapped_column(Boolean, default=True)
    has_air_conditioner: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional info"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Is room available"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TASHKENT_TZ),
        onupdate=lambda: datetime.now(TASHKENT_TZ),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name='{self.name}', building='{self.building}')>"
    
    @property
    def full_name(self) -> str:
        if self.building:
            return f"{self.name} ({self.building})"
        return self.name
