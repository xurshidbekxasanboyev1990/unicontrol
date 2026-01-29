"""
UniControl - Canteen Service
============================
Business logic for canteen (oshxona) operations.

This service handles:
- Menu categories CRUD
- Menu items CRUD
- Order creation and management
- Order status updates
- Statistics and reports

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.canteen import MenuCategory, MenuItem, Order, OrderItem, OrderStatus
from app.schemas.canteen import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate,
    CanteenStats
)


class CanteenService:
    """
    Service class for canteen operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CATEGORY OPERATIONS ====================
    
    async def get_categories(self, active_only: bool = True) -> List[MenuCategory]:
        """
        Get all menu categories.
        
        Args:
            active_only: Only return active categories
            
        Returns:
            List of categories
        """
        query = select(MenuCategory).order_by(MenuCategory.sort_order)
        
        if active_only:
            query = query.where(MenuCategory.is_active == True)
        
        result = await self.db.execute(query)
        categories = result.scalars().all()
        
        # Count items for each category
        for cat in categories:
            items_count_query = select(func.count(MenuItem.id)).where(
                MenuItem.category_id == cat.id
            )
            result = await self.db.execute(items_count_query)
            cat.items_count = result.scalar() or 0
        
        return categories
    
    async def get_category(self, category_id: int) -> Optional[MenuCategory]:
        """Get category by ID."""
        query = select(MenuCategory).where(MenuCategory.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_category(self, data: CategoryCreate) -> MenuCategory:
        """
        Create a new menu category.
        """
        category = MenuCategory(
            name=data.name,
            description=data.description,
            icon=data.icon,
            color=data.color,
            sort_order=data.sort_order,
            is_active=data.is_active
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def update_category(
        self, 
        category_id: int, 
        data: CategoryUpdate
    ) -> Optional[MenuCategory]:
        """Update a category."""
        category = await self.get_category(category_id)
        if not category:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete a category."""
        category = await self.get_category(category_id)
        if not category:
            return False
        
        await self.db.delete(category)
        await self.db.commit()
        
        return True
    
    # ==================== MENU ITEM OPERATIONS ====================
    
    async def get_menu_items(
        self,
        category_id: Optional[int] = None,
        is_available: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[MenuItem]:
        """
        Get menu items with optional filters.
        
        Args:
            category_id: Filter by category
            is_available: Filter by availability
            search: Search in name/description
            
        Returns:
            List of menu items
        """
        query = select(MenuItem).options(
            selectinload(MenuItem.category)
        ).order_by(MenuItem.name)
        
        if category_id:
            query = query.where(MenuItem.category_id == category_id)
        
        if is_available is not None:
            query = query.where(MenuItem.is_available == is_available)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    MenuItem.name.ilike(search_term),
                    MenuItem.description.ilike(search_term)
                )
            )
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Add category name
        for item in items:
            if item.category:
                item.category_name = item.category.name
        
        return items
    
    async def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID."""
        query = select(MenuItem).options(
            selectinload(MenuItem.category)
        ).where(MenuItem.id == item_id)
        
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if item and item.category:
            item.category_name = item.category.name
        
        return item
    
    async def create_menu_item(self, data: MenuItemCreate) -> MenuItem:
        """
        Create a new menu item.
        """
        # Verify category exists
        category = await self.get_category(data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
        
        item = MenuItem(
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            price=data.price,
            image_url=data.image_url,
            is_available=data.is_available,
            is_vegetarian=data.is_vegetarian,
            is_halal=data.is_halal,
            calories=data.calories,
            preparation_time=data.preparation_time
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        item.category_name = category.name
        
        return item
    
    async def update_menu_item(
        self, 
        item_id: int, 
        data: MenuItemUpdate
    ) -> Optional[MenuItem]:
        """Update a menu item."""
        item = await self.get_menu_item(item_id)
        if not item:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Verify category if changing
        if 'category_id' in update_data:
            category = await self.get_category(update_data['category_id'])
            if not category:
                raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def delete_menu_item(self, item_id: int) -> bool:
        """Delete a menu item."""
        item = await self.get_menu_item(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.commit()
        
        return True
    
    # ==================== ORDER OPERATIONS ====================
    
    async def _generate_order_number(self) -> str:
        """Generate unique order number for today."""
        today = date.today()
        
        # Count orders today
        count_query = select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Format: #001, #002, etc.
        return f"#{count + 1:03d}"
    
    async def create_order(self, user_id: int, data: OrderCreate) -> Order:
        """
        Create a new order.
        
        Args:
            user_id: Customer user ID
            data: Order creation data with items
            
        Returns:
            Created order
        """
        # Generate order number
        order_number = await self._generate_order_number()
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.PENDING,
            notes=data.notes,
            total_amount=Decimal("0")
        )
        
        self.db.add(order)
        await self.db.flush()  # Get order ID
        
        total_amount = Decimal("0")
        
        # Add order items
        for item_data in data.items:
            menu_item = await self.get_menu_item(item_data.menu_item_id)
            if not menu_item:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Menyu elementi topilmadi: {item_data.menu_item_id}"
                )
            
            if not menu_item.is_available:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{menu_item.name}' hozirda mavjud emas"
                )
            
            item_total = menu_item.price * item_data.quantity
            total_amount += item_total
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=item_data.quantity,
                unit_price=menu_item.price,
                total_price=item_total,
                item_name=menu_item.name
            )
            
            self.db.add(order_item)
        
        order.total_amount = total_amount
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return await self.get_order(order.id)
    
    async def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items."""
        query = select(Order).options(
            selectinload(Order.items),
            selectinload(Order.user)
        ).where(Order.id == order_id)
        
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if order and order.user:
            order.user_name = order.user.full_name
        
        return order
    
    async def get_user_orders(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Order], int]:
        """
        Get orders for a specific user.
        
        Returns:
            Tuple of (orders list, total count)
        """
        # Count total
        count_query = select(func.count(Order.id)).where(Order.user_id == user_id)
        result = await self.db.execute(count_query)
        total = result.scalar() or 0
        
        # Get orders
        offset = (page - 1) * page_size
        query = select(Order).options(
            selectinload(Order.items)
        ).where(
            Order.user_id == user_id
        ).order_by(
            desc(Order.created_at)
        ).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        return orders, total
    
    async def get_all_orders(
        self,
        status: Optional[OrderStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Order], int]:
        """
        Get all orders with filters (admin).
        
        Returns:
            Tuple of (orders list, total count)
        """
        # Base query
        base_query = select(Order)
        count_query = select(func.count(Order.id))
        
        # Apply filters
        filters = []
        if status:
            filters.append(Order.status == status)
        if date_from:
            filters.append(func.date(Order.created_at) >= date_from)
        if date_to:
            filters.append(func.date(Order.created_at) <= date_to)
        
        if filters:
            base_query = base_query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Count
        result = await self.db.execute(count_query)
        total = result.scalar() or 0
        
        # Get orders
        offset = (page - 1) * page_size
        query = base_query.options(
            selectinload(Order.items),
            selectinload(Order.user)
        ).order_by(
            desc(Order.created_at)
        ).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        for order in orders:
            if order.user:
                order.user_name = order.user.full_name
        
        return orders, total
    
    async def update_order_status(
        self,
        order_id: int,
        status: OrderStatus
    ) -> Optional[Order]:
        """
        Update order status.
        
        Args:
            order_id: Order ID
            status: New status
            
        Returns:
            Updated order
        """
        order = await self.get_order(order_id)
        if not order:
            return None
        
        order.status = status
        
        # Set completion time if completed
        if status == OrderStatus.COMPLETED:
            order.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    # ==================== STATISTICS ====================
    
    async def get_stats(self) -> CanteenStats:
        """
        Get canteen statistics for today.
        
        Returns:
            Statistics object
        """
        today = date.today()
        
        # Orders today
        orders_today_query = select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
        result = await self.db.execute(orders_today_query)
        total_orders_today = result.scalar() or 0
        
        # Revenue today
        revenue_query = select(func.sum(Order.total_amount)).where(
            and_(
                func.date(Order.created_at) == today,
                Order.status.in_([OrderStatus.COMPLETED, OrderStatus.READY, OrderStatus.PREPARING])
            )
        )
        result = await self.db.execute(revenue_query)
        total_revenue_today = result.scalar() or Decimal("0")
        
        # Status counts
        async def count_by_status(status: OrderStatus) -> int:
            query = select(func.count(Order.id)).where(
                and_(
                    func.date(Order.created_at) == today,
                    Order.status == status
                )
            )
            result = await self.db.execute(query)
            return result.scalar() or 0
        
        pending = await count_by_status(OrderStatus.PENDING)
        preparing = await count_by_status(OrderStatus.PREPARING)
        ready = await count_by_status(OrderStatus.READY)
        completed = await count_by_status(OrderStatus.COMPLETED)
        
        # Popular items (top 5)
        popular_query = select(
            OrderItem.item_name,
            func.sum(OrderItem.quantity).label('total_qty')
        ).join(Order).where(
            func.date(Order.created_at) == today
        ).group_by(OrderItem.item_name).order_by(
            desc('total_qty')
        ).limit(5)
        
        result = await self.db.execute(popular_query)
        popular_items = [
            {"name": row.item_name, "quantity": row.total_qty}
            for row in result.all()
        ]
        
        return CanteenStats(
            total_orders_today=total_orders_today,
            total_revenue_today=total_revenue_today,
            pending_orders=pending,
            preparing_orders=preparing,
            ready_orders=ready,
            completed_orders_today=completed,
            popular_items=popular_items,
            orders_by_hour=[]  # Can be implemented later
        )
