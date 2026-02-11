"""
Landing Settings API Routes
============================
Manage landing page content. Public GET (no auth), PUT requires superadmin.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.models.user import User, UserRole
from app.models.landing import LandingSettings
from app.core.dependencies import get_current_active_user, require_superadmin

router = APIRouter()


# ===== Schemas =====

class LandingSettingsResponse(BaseModel):
    """Full landing settings response"""
    hero_stats: Dict[str, Any] = {}
    social_links: List[Dict[str, Any]] = []
    team_members: List[Dict[str, Any]] = []
    contact_info: Dict[str, Any] = {}
    about_stats: Dict[str, Any] = {}
    feature_cards: List[Dict[str, Any]] = []
    trusted_by: List[Dict[str, Any]] = []
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class LandingSettingsUpdate(BaseModel):
    """Update landing settings — any subset of fields"""
    hero_stats: Optional[Dict[str, Any]] = None
    social_links: Optional[List[Dict[str, Any]]] = None
    team_members: Optional[List[Dict[str, Any]]] = None
    contact_info: Optional[Dict[str, Any]] = None
    about_stats: Optional[Dict[str, Any]] = None
    feature_cards: Optional[List[Dict[str, Any]]] = None
    trusted_by: Optional[List[Dict[str, Any]]] = None


# ===== Helpers =====

async def get_or_create_landing(db: AsyncSession) -> LandingSettings:
    """Get singleton landing settings row, create if not exists."""
    result = await db.execute(select(LandingSettings).where(LandingSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = LandingSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


def settings_to_dict(s: LandingSettings) -> dict:
    """Convert model to response dict"""
    return {
        "hero_stats": s.hero_stats or {},
        "social_links": s.social_links or [],
        "team_members": s.team_members or [],
        "contact_info": s.contact_info or {},
        "about_stats": s.about_stats or {},
        "feature_cards": s.feature_cards or [],
        "trusted_by": s.trusted_by or [],
        "updated_at": s.updated_at.isoformat() if s.updated_at else None
    }


# ===== PUBLIC endpoints (no auth) =====

@router.get("/public")
async def get_landing_public(db: AsyncSession = Depends(get_db)):
    """
    Get landing page data — PUBLIC, no authentication required.
    Used by the public landing page to display dynamic content.
    """
    settings = await get_or_create_landing(db)
    return settings_to_dict(settings)


# ===== ADMIN endpoints (superadmin only) =====

@router.get("")
async def get_landing_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Get full landing settings (superadmin only)"""
    settings = await get_or_create_landing(db)
    return settings_to_dict(settings)


@router.put("")
async def update_landing_settings(
    data: LandingSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update landing settings (superadmin only)"""
    settings = await get_or_create_landing(db)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return settings_to_dict(settings)


# === Individual section updates ===

@router.put("/hero-stats")
async def update_hero_stats(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update hero section stats"""
    settings = await get_or_create_landing(db)
    settings.hero_stats = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Hero stats yangilandi", "hero_stats": settings.hero_stats}


@router.put("/social-links")
async def update_social_links(
    data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update social links"""
    settings = await get_or_create_landing(db)
    settings.social_links = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Ijtimoiy tarmoqlar yangilandi", "social_links": settings.social_links}


@router.put("/team-members")
async def update_team_members(
    data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update team members"""
    settings = await get_or_create_landing(db)
    settings.team_members = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Jamoa a'zolari yangilandi", "team_members": settings.team_members}


@router.put("/contact-info")
async def update_contact_info(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update contact info"""
    settings = await get_or_create_landing(db)
    settings.contact_info = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Aloqa ma'lumotlari yangilandi", "contact_info": settings.contact_info}


@router.put("/feature-cards")
async def update_feature_cards(
    data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update feature cards"""
    settings = await get_or_create_landing(db)
    settings.feature_cards = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Kartalar yangilandi", "feature_cards": settings.feature_cards}


@router.put("/about-stats")
async def update_about_stats(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update about section stats"""
    settings = await get_or_create_landing(db)
    settings.about_stats = data
    await db.commit()
    await db.refresh(settings)
    return {"message": "Biz haqimizda yangilandi", "about_stats": settings.about_stats}
