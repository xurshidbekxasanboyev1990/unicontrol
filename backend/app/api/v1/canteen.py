"""
UniControl - Canteen Routes
===========================
Canteen (oshxona) API endpoints.

This module provides:
- Menu categories CRUD (admin)
- Menu items CRUD (admin)
- Menu viewing (students)
- Order creation (students)
- Order management (admin)
- Statistics (admin)

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.canteen_service import CanteenService
from app.schemas.canteen import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemListResponse,
    OrderCreate, OrderResponse, OrderListResponse, OrderStatusUpdate,
    CanteenStats
)
from app.models.canteen import OrderStatus
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter()


# ==================== CATEGORY ENDPOINTS ====================

@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    active_only: bool = Query(True, description="Faqat faol kategoriyalar"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all menu categories.
    
    - **active_only**: Only return active categories (default: True)
    """
    service = CanteenService(db)
    categories = await service.get_categories(active_only=active_only)
    
    return CategoryListResponse(
        items=[CategoryResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            icon=c.icon,
            color=c.color,
            sort_order=c.sort_order,
            is_active=c.is_active,
            created_at=c.created_at,
            items_count=getattr(c, 'items_count', 0)
        ) for c in categories],
        total=len(categories)
    )


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new menu category (admin only).
    
    - **name**: Category name (required)
    - **description**: Category description
    - **icon**: Icon name for UI
    - **color**: Color hex code
    - **sort_order**: Display order
    """
    service = CanteenService(db)
    category = await service.create_category(data)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        icon=category.icon,
        color=category.color,
        sort_order=category.sort_order,
        is_active=category.is_active,
        created_at=category.created_at,
        items_count=0
    )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a menu category (admin only).
    """
    service = CanteenService(db)
    category = await service.update_category(category_id, data)
    
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        icon=category.icon,
        color=category.color,
        sort_order=category.sort_order,
        is_active=category.is_active,
        created_at=category.created_at,
        items_count=getattr(category, 'items_count', 0)
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a menu category (admin only).
    
    Warning: This will also delete all menu items in this category!
    """
    service = CanteenService(db)
    deleted = await service.delete_category(category_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    
    return None


# ==================== MENU ITEM ENDPOINTS ====================

@router.get("/menu", response_model=MenuItemListResponse)
async def get_menu(
    category_id: Optional[int] = Query(None, description="Kategoriya filtri"),
    is_available: Optional[bool] = Query(None, description="Mavjudlik filtri"),
    search: Optional[str] = Query(None, max_length=100, description="Qidiruv"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get menu items with optional filters.
    
    - **category_id**: Filter by category
    - **is_available**: Filter by availability
    - **search**: Search in name/description
    """
    service = CanteenService(db)
    items = await service.get_menu_items(
        category_id=category_id,
        is_available=is_available,
        search=search
    )
    
    return MenuItemListResponse(
        items=[MenuItemResponse(
            id=item.id,
            category_id=item.category_id,
            category_name=getattr(item, 'category_name', None),
            name=item.name,
            description=item.description,
            price=item.price,
            image_url=item.image_url,
            is_available=item.is_available,
            is_vegetarian=item.is_vegetarian,
            is_halal=item.is_halal,
            calories=item.calories,
            preparation_time=item.preparation_time,
            created_at=item.created_at,
            updated_at=item.updated_at
        ) for item in items],
        total=len(items)
    )


@router.get("/menu/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get menu item by ID.
    """
    service = CanteenService(db)
    item = await service.get_menu_item(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Menyu elementi topilmadi")
    
    return MenuItemResponse(
        id=item.id,
        category_id=item.category_id,
        category_name=getattr(item, 'category_name', None),
        name=item.name,
        description=item.description,
        price=item.price,
        image_url=item.image_url,
        is_available=item.is_available,
        is_vegetarian=item.is_vegetarian,
        is_halal=item.is_halal,
        calories=item.calories,
        preparation_time=item.preparation_time,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.post("/menu", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    data: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new menu item (admin only).
    """
    service = CanteenService(db)
    item = await service.create_menu_item(data)
    
    return MenuItemResponse(
        id=item.id,
        category_id=item.category_id,
        category_name=getattr(item, 'category_name', None),
        name=item.name,
        description=item.description,
        price=item.price,
        image_url=item.image_url,
        is_available=item.is_available,
        is_vegetarian=item.is_vegetarian,
        is_halal=item.is_halal,
        calories=item.calories,
        preparation_time=item.preparation_time,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.put("/menu/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a menu item (admin only).
    """
    service = CanteenService(db)
    item = await service.update_menu_item(item_id, data)
    
    if not item:
        raise HTTPException(status_code=404, detail="Menyu elementi topilmadi")
    
    return MenuItemResponse(
        id=item.id,
        category_id=item.category_id,
        category_name=getattr(item, 'category_name', None),
        name=item.name,
        description=item.description,
        price=item.price,
        image_url=item.image_url,
        is_available=item.is_available,
        is_vegetarian=item.is_vegetarian,
        is_halal=item.is_halal,
        calories=item.calories,
        preparation_time=item.preparation_time,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a menu item (admin only).
    """
    service = CanteenService(db)
    deleted = await service.delete_menu_item(item_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Menyu elementi topilmadi")
    
    return None


# ==================== ORDER ENDPOINTS ====================

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new order.
    
    - **items**: List of menu items with quantities (required)
    - **notes**: Special requests/notes (optional)
    """
    service = CanteenService(db)
    order = await service.create_order(current_user.id, data)
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        user_name=getattr(order, 'user_name', None),
        status=order.status,
        total_amount=order.total_amount,
        notes=order.notes,
        items=[{
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        } for item in order.items],
        items_count=order.items_count,
        created_at=order.created_at,
        completed_at=order.completed_at
    )


@router.get("/orders/my", response_model=OrderListResponse)
async def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's orders.
    """
    service = CanteenService(db)
    orders, total = await service.get_user_orders(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return OrderListResponse(
        items=[OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            notes=order.notes,
            items=[{
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            } for item in order.items],
            items_count=order.items_count,
            created_at=order.created_at,
            completed_at=order.completed_at
        ) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/orders", response_model=OrderListResponse)
async def get_all_orders(
    status: Optional[OrderStatus] = Query(None, description="Status filtri"),
    date_from: Optional[date] = Query(None, description="Boshlanish sanasi"),
    date_to: Optional[date] = Query(None, description="Tugash sanasi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all orders with filters (admin only).
    """
    service = CanteenService(db)
    orders, total = await service.get_all_orders(
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size
    )
    
    return OrderListResponse(
        items=[OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            user_name=getattr(order, 'user_name', None),
            status=order.status,
            total_amount=order.total_amount,
            notes=order.notes,
            items=[{
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            } for item in order.items],
            items_count=order.items_count,
            created_at=order.created_at,
            completed_at=order.completed_at
        ) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update order status (admin only).
    
    Status transitions:
    - pending → preparing
    - preparing → ready
    - ready → completed
    - any → cancelled
    """
    service = CanteenService(db)
    order = await service.update_order_status(order_id, data.status)
    
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        user_name=getattr(order, 'user_name', None),
        status=order.status,
        total_amount=order.total_amount,
        notes=order.notes,
        items=[{
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        } for item in order.items],
        items_count=order.items_count,
        created_at=order.created_at,
        completed_at=order.completed_at
    )


# ==================== STATISTICS ====================

@router.get("/stats", response_model=CanteenStats)
async def get_canteen_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get canteen statistics for today (admin only).
    
    Returns:
    - Total orders today
    - Total revenue today
    - Orders by status
    - Popular items
    """
    service = CanteenService(db)
    return await service.get_stats()
