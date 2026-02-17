"""
UniControl - Canteen Model
===========================
Database models for university canteen management.

This module handles:
- Menu categories (drinks, meals, snacks, etc.)
- Menu items with prices and availability
- Student orders and order items
- Order status tracking

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Text, Boolean, Numeric, Enum as SQLEnum
)
from sqlalchemy.orm import relationship

from app.config import TASHKENT_TZ
from app.database import Base


class OrderStatus(str, Enum):
    """
    Order status enumeration.
    """
    PENDING = "pending"          # Kutilmoqda
    PREPARING = "preparing"      # Tayyorlanmoqda
    READY = "ready"              # Tayyor
    COMPLETED = "completed"      # Olib ketildi
    CANCELLED = "cancelled"      # Bekor qilindi


class MenuCategory(Base):
    """
    Menu category model.
    
    Categories for organizing menu items.
    E.g., Ichimliklar, Asosiy taomlar, Salatlar, etc.
    
    Attributes:
        id: Primary key
        name: Category name
        description: Category description
        icon: Icon name for UI (optional)
        color: Color hex code for UI (optional)
        sort_order: Display order
        is_active: Whether category is active
        created_at: Creation timestamp
    """
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="Kategoriya nomi")
    description = Column(Text, nullable=True, comment="Kategoriya tavsifi")
    icon = Column(String(50), nullable=True, default="Utensils", comment="Icon nomi")
    color = Column(String(20), nullable=True, default="#10b981", comment="Rang kodi")
    sort_order = Column(Integer, default=0, comment="Tartib raqami")
    is_active = Column(Boolean, default=True, comment="Faollik holati")
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MenuCategory(id={self.id}, name='{self.name}')>"


class MenuItem(Base):
    """
    Menu item model.
    
    Individual food/drink items available in the canteen.
    
    Attributes:
        id: Primary key
        category_id: Parent category
        name: Item name
        description: Item description
        price: Price in UZS
        image_url: Item image URL (optional)
        is_available: Current availability
        is_vegetarian: Vegetarian flag
        is_halal: Halal flag
        calories: Calorie count (optional)
        preparation_time: Time in minutes (optional)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Category
    category_id = Column(
        Integer, 
        ForeignKey("menu_categories.id", ondelete="CASCADE"),
        nullable=False,
        comment="Kategoriya ID"
    )
    
    # Basic info
    name = Column(String(200), nullable=False, comment="Taom nomi")
    description = Column(Text, nullable=True, comment="Tavsif")
    price = Column(Numeric(12, 2), nullable=False, comment="Narxi (so'm)")
    image_url = Column(String(500), nullable=True, comment="Rasm URL")
    
    # Availability
    is_available = Column(Boolean, default=True, comment="Mavjudlik")
    
    # Additional info
    is_vegetarian = Column(Boolean, default=False, comment="Vegetarian")
    is_halal = Column(Boolean, default=True, comment="Halol")
    calories = Column(Integer, nullable=True, comment="Kaloriya")
    preparation_time = Column(Integer, nullable=True, comment="Tayyorlanish vaqti (daqiqa)")
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), onupdate=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None))
    
    # Relationships
    category = relationship("MenuCategory", back_populates="items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"


class Order(Base):
    """
    Order model.
    
    Represents a student's order.
    
    Attributes:
        id: Primary key
        order_number: Human-readable order number (e.g., #001)
        user_id: Customer user ID
        status: Order status
        total_amount: Total price
        notes: Special requests/notes
        created_at: Order timestamp
        completed_at: Completion timestamp
    """
    __tablename__ = "canteen_orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Order number
    order_number = Column(
        String(20), 
        unique=True, 
        nullable=False,
        comment="Buyurtma raqami"
    )
    
    # Customer
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    
    # Status
    status = Column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="Buyurtma holati"
    )
    
    # Financials
    total_amount = Column(Numeric(12, 2), nullable=False, default=0, comment="Jami summa")
    
    # Notes
    notes = Column(Text, nullable=True, comment="Izohlar")
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(TASHKENT_TZ).replace(tzinfo=None), comment="Yaratilgan vaqt")
    completed_at = Column(DateTime, nullable=True, comment="Bajarilgan vaqt")
    
    # Relationships
    user = relationship("User", backref="canteen_orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status={self.status})>"
    
    @property
    def items_count(self) -> int:
        """Total number of items in order."""
        return sum(item.quantity for item in self.items) if self.items else 0


class OrderItem(Base):
    """
    Order item model.
    
    Individual items within an order.
    
    Attributes:
        id: Primary key
        order_id: Parent order
        menu_item_id: Ordered menu item
        quantity: Quantity ordered
        unit_price: Price at time of order
        total_price: Quantity * unit_price
    """
    __tablename__ = "canteen_order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Parent order
    order_id = Column(
        Integer,
        ForeignKey("canteen_orders.id", ondelete="CASCADE"),
        nullable=False,
        comment="Buyurtma ID"
    )
    
    # Menu item
    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.id", ondelete="SET NULL"),
        nullable=True,
        comment="Menyu elementi ID"
    )
    
    # Quantity and price
    quantity = Column(Integer, nullable=False, default=1, comment="Miqdor")
    unit_price = Column(Numeric(12, 2), nullable=False, comment="Birlik narxi")
    total_price = Column(Numeric(12, 2), nullable=False, comment="Jami narxi")
    
    # Item name snapshot (in case menu item is deleted)
    item_name = Column(String(200), nullable=False, comment="Taom nomi (snapshot)")
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, item='{self.item_name}', qty={self.quantity})>"
