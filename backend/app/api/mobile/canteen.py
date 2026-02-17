"""
UniControl - Mobile Canteen Routes
===================================
Mobile endpoints for canteen/food ordering.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.canteen import MenuCategory, MenuItem, Order, OrderItem, OrderStatus
from app.core.dependencies import get_current_active_user

router = APIRouter()


class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = 1


class CreateOrderRequest(BaseModel):
    items: list[OrderItemRequest]
    notes: Optional[str] = None


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get menu categories."""
    result = await db.execute(
        select(MenuCategory).where(MenuCategory.is_active == True).order_by(MenuCategory.sort_order)
    )
    categories = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "icon": c.icon,
            "color": c.color,
        }
        for c in categories
    ]


@router.get("/menu")
async def get_menu(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    available_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get menu items."""
    query = select(MenuItem).where(MenuItem.is_active == True)

    if category_id:
        query = query.where(MenuItem.category_id == category_id)
    if search:
        query = query.where(MenuItem.name.ilike(f"%{search}%"))
    if available_only:
        query = query.where(MenuItem.is_available == True)

    result = await db.execute(query.order_by(MenuItem.name))
    items = result.scalars().all()

    menu_items = []
    for item in items:
        # Get category name
        cat = None
        if item.category_id:
            cat_res = await db.execute(select(MenuCategory).where(MenuCategory.id == item.category_id))
            cat_obj = cat_res.scalar_one_or_none()
            cat = cat_obj.name if cat_obj else None

        menu_items.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price) if item.price else 0,
            "image": item.image,
            "category_id": item.category_id,
            "category_name": cat,
            "is_available": item.is_available,
            "is_vegetarian": getattr(item, 'is_vegetarian', False),
            "preparation_time": getattr(item, 'preparation_time', None),
        })

    return {"items": menu_items}


@router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new order."""
    if not request.items:
        raise HTTPException(status_code=400, detail="Buyurtma bo'sh bo'lishi mumkin emas")

    total = 0
    order_items_data = []

    for item_req in request.items:
        menu_item = (await db.execute(
            select(MenuItem).where(MenuItem.id == item_req.menu_item_id)
        )).scalar_one_or_none()

        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_req.menu_item_id} topilmadi")
        if not menu_item.is_available:
            raise HTTPException(status_code=400, detail=f"{menu_item.name} mavjud emas")

        subtotal = float(menu_item.price or 0) * item_req.quantity
        total += subtotal
        order_items_data.append({
            "menu_item": menu_item,
            "quantity": item_req.quantity,
            "price": float(menu_item.price or 0),
            "subtotal": subtotal,
        })

    order = Order(
        user_id=current_user.id,
        order_number=f"M-{current_user.id}-{int(__import__('time').time())}",
        total_amount=total,
        status=OrderStatus.PENDING,
        notes=request.notes,
    )
    db.add(order)
    await db.flush()

    for oid in order_items_data:
        oi = OrderItem(
            order_id=order.id,
            menu_item_id=oid["menu_item"].id,
            quantity=oid["quantity"],
            unit_price=oid["price"],
            total_price=oid["subtotal"],
            item_name=oid["menu_item"].name,
        )
        db.add(oi)

    await db.commit()
    await db.refresh(order)

    return {
        "success": True,
        "order_id": order.id,
        "total": total,
        "status": "pending",
        "message": "Buyurtma qabul qilindi",
    }


@router.get("/orders")
async def get_my_orders(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's orders."""
    query = select(Order).where(Order.user_id == current_user.id)

    if status:
        try:
            st = OrderStatus(status)
            query = query.where(Order.status == st)
        except ValueError:
            pass

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(query.order_by(desc(Order.created_at)).offset(offset).limit(page_size))
    orders = result.scalars().all()

    items = []
    for o in orders:
        # Get order items
        oi_result = await db.execute(select(OrderItem).where(OrderItem.order_id == o.id))
        oi_list = oi_result.scalars().all()

        order_items = []
        for oi in oi_list:
            order_items.append({
                "name": oi.item_name or "Noma'lum",
                "quantity": oi.quantity,
                "price": float(oi.unit_price) if oi.unit_price else 0,
                "total": float(oi.total_price) if oi.total_price else 0,
            })

        items.append({
            "id": o.id,
            "order_number": o.order_number,
            "total": float(o.total_amount) if o.total_amount else 0,
            "status": o.status.value if o.status else "pending",
            "notes": o.notes,
            "created_at": str(o.created_at) if o.created_at else None,
            "items": order_items,
            "item_count": len(order_items),
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}
