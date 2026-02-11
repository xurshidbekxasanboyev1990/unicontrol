"""
UniControl - Push Notification Routes
=====================================
Firebase push notification endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.config import settings

router = APIRouter()


class PushTokenRegister(BaseModel):
    """Register push token request."""
    token: str
    device_type: str = "android"  # android, ios, web


class SendPushRequest(BaseModel):
    """Send push notification request."""
    user_ids: list[int]
    title: str
    body: str
    data: Optional[dict] = None


class PushNotificationService:
    """Firebase push notification service."""
    
    def __init__(self):
        self.firebase_initialized = False
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase."""
        if not settings.FIREBASE_CREDENTIALS_PATH:
            return
        
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            
            self.firebase_initialized = True
        except Exception as e:
            logger.warning(f"Firebase init error: {e}")
    
    async def send_notification(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> dict:
        """Send push notification."""
        if not self.firebase_initialized:
            return {"success": False, "error": "Firebase not initialized"}
        
        try:
            from firebase_admin import messaging
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> dict:
        """Send push to topic."""
        if not self.firebase_initialized:
            return {"success": False, "error": "Firebase not initialized"}
        
        try:
            from firebase_admin import messaging
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            return {"success": True, "message_id": response}
        except Exception as e:
            return {"success": False, "error": str(e)}


push_service = PushNotificationService()


@router.post("/register")
async def register_push_token(
    request: PushTokenRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Register device push token.
    """
    # Store token in user's device_tokens (JSON field)
    if not current_user.device_tokens:
        current_user.device_tokens = []
    
    # Add token if not exists
    token_exists = any(
        t.get("token") == request.token 
        for t in current_user.device_tokens
    )
    
    if not token_exists:
        current_user.device_tokens.append({
            "token": request.token,
            "device_type": request.device_type
        })
        await db.commit()
    
    return {"message": "Token registered"}


@router.delete("/unregister")
async def unregister_push_token(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unregister device push token.
    """
    if current_user.device_tokens:
        current_user.device_tokens = [
            t for t in current_user.device_tokens
            if t.get("token") != token
        ]
        await db.commit()
    
    return {"message": "Token unregistered"}


@router.post("/send")
async def send_push_notification(
    request: SendPushRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Send push notification to users.
    
    Requires admin role.
    """
    from sqlalchemy import select
    
    # Get users' tokens
    result = await db.execute(
        select(User).where(User.id.in_(request.user_ids))
    )
    users = result.scalars().all()
    
    # Collect all tokens
    tokens = []
    for user in users:
        if user.device_tokens:
            for device in user.device_tokens:
                if device.get("token"):
                    tokens.append(device["token"])
    
    if not tokens:
        return {"success": False, "error": "No device tokens found"}
    
    # Send notification
    result = await push_service.send_notification(
        tokens=tokens,
        title=request.title,
        body=request.body,
        data=request.data
    )
    
    return result


@router.post("/send-topic")
async def send_to_topic(
    topic: str = Query(...),
    title: str = Query(...),
    body: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Send push notification to topic.
    
    Requires admin role.
    """
    result = await push_service.send_to_topic(
        topic=topic,
        title=title,
        body=body
    )
    
    return result


@router.post("/subscribe")
async def subscribe_to_topic(
    topic: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subscribe user to topic.
    """
    if not push_service.firebase_initialized:
        return {"success": False, "error": "Firebase not initialized"}
    
    if not current_user.device_tokens:
        return {"success": False, "error": "No device tokens registered"}
    
    try:
        from firebase_admin import messaging
        
        tokens = [t["token"] for t in current_user.device_tokens if t.get("token")]
        
        response = messaging.subscribe_to_topic(tokens, topic)
        
        return {
            "success": True,
            "success_count": response.success_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/unsubscribe")
async def unsubscribe_from_topic(
    topic: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unsubscribe user from topic.
    """
    if not push_service.firebase_initialized:
        return {"success": False, "error": "Firebase not initialized"}
    
    if not current_user.device_tokens:
        return {"success": False, "error": "No device tokens registered"}
    
    try:
        from firebase_admin import messaging
        
        tokens = [t["token"] for t in current_user.device_tokens if t.get("token")]
        
        response = messaging.unsubscribe_from_topic(tokens, topic)
        
        return {
            "success": True,
            "success_count": response.success_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/status")
async def get_push_status():
    """
    Get push notification service status.
    """
    return {
        "firebase_initialized": push_service.firebase_initialized,
        "status": "operational" if push_service.firebase_initialized else "not_configured"
    }
