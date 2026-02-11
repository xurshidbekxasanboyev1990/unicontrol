"""
UniControl - Canteen Schemas
============================
Pydantic schemas for canteen (oshxona) operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.canteen import OrderStatus


# ==================== CATEGORY SCHEMAS ====================

class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(default="Utensils")
    color: Optional[str] = Field(default="#10b981")
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int
    created_at: datetime
    items_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    items: List[CategoryResponse]
    total: int


# ==================== MENU ITEM SCHEMAS ====================

class MenuItemBase(BaseModel):
    """Base menu item schema."""
    category_id: int
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    image_url: Optional[str] = None
    is_available: bool = Field(default=True)
    is_vegetarian: bool = Field(default=False)
    is_halal: bool = Field(default=True)
    calories: Optional[int] = Field(None, ge=0)
    preparation_time: Optional[int] = Field(None, ge=0)


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item."""
    pass


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    is_halal: Optional[bool] = None
    calories: Optional[int] = Field(None, ge=0)
    preparation_time: Optional[int] = Field(None, ge=0)


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""
    id: int
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MenuItemListResponse(BaseModel):
    """Schema for menu item list response."""
    items: List[MenuItemResponse]
    total: int


# ==================== ORDER SCHEMAS ====================

class OrderItemCreate(BaseModel):
    """Schema for order item in order creation."""
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    items: List[OrderItemCreate] = Field(..., min_length=1)
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: int
    menu_item_id: Optional[int] = None
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    order_number: str
    user_id: int
    user_name: Optional[str] = None
    status: OrderStatus
    total_amount: Decimal
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    items_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Schema for order list response."""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


# ==================== STATISTICS SCHEMAS ====================

class CanteenStats(BaseModel):
    """Schema for canteen statistics."""
    total_orders_today: int = 0
    total_revenue_today: Decimal = Decimal("0")
    pending_orders: int = 0
    preparing_orders: int = 0
    ready_orders: int = 0
    completed_orders_today: int = 0
    popular_items: List[dict] = []
    orders_by_hour: List[dict] = []
